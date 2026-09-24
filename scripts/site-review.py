#!/usr/bin/env python3
"""Static product/QA review for the generated Jekyll site.

This complements smoke-test.rb: it checks rendered controls, landmarks,
accessible names, current-page state, and the high-value shell routes without
requiring a browser runtime or third-party packages.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "_site"
KNOWN_HISTORICAL_FENCE_ROUTES = {
    "2020/07/02/书签中的一些工具整理/index.html",
    "2020/07/09/Log4cxx/index.html",
    "2020/07/10/Log4cxx-API/index.html",
    "2020/09/13/摄影-Book-Reading-notes-美国纽约摄影学院摄影教材/index.html",
    "2022/01/01/吾爱破解-培训第八-九课-短兵相接-深入浅出探讨脱壳细节-笔记/index.html",
    "2023/04/09/OS-Linux-环境变量-LD_LIBRARY_PATH/index.html",
    "2024/02/20/通用方式实现Map/index.html",
    "2024/07/12/Code-Logger-替换标准输出和标准错误-并通过宏使能输出/index.html",
    "2026/06/01/Model-Sentence-Transformers-models-Sentence-BERT-模型/index.html",
    "2026/06/02/AI-coding-agent-OpenCode/index.html",
    "2026/06/03/Yuxi-Know/index.html",
    "2026/06/10/Model-MiniCPM5-1B-Deploy-Ollama(Docker)/index.html",
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.lang: str | None = None
        self.main_ids: list[str] = []
        self.h1 = 0
        self.links: list[dict[str, str]] = []
        self.buttons: list[dict[str, str]] = []
        self.controls: list[tuple[str, dict[str, str]]] = []
        self.labels: set[str] = set()
        self.aria_current: list[str] = []
        self.anchor_controls: list[dict[str, str]] = []
        self.empty_anchors: list[str] = []
        self.invalid_hrefs: list[str] = []
        self.fence_in_list = False
        self._list_depth = 0
        self._button_stack: list[int] = []
        self._button_text: dict[int, list[str]] = {}
        self._pre_depth = 0

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}
        if tag == "html" and self.lang is None:
            self.lang = attrs.get("lang")
        if tag == "pre":
            self._pre_depth += 1
        if self._pre_depth == 0 and attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag == "main":
            self.main_ids.append(attrs.get("id", ""))
        if tag == "h1":
            self.h1 += 1
        if tag == "a":
            self.links.append(attrs)
            href = attrs.get("href", "")
            if not href:
                self.empty_anchors.append(href)
            elif any(char.isspace() for char in href):
                self.invalid_hrefs.append(href)
            if attrs.get("aria-current"):
                self.aria_current.append(attrs.get("href", ""))
        if tag in {"ol", "ul"}:
            self._list_depth += 1
        if tag == "button":
            index = len(self.buttons)
            self.buttons.append(attrs)
            self._button_stack.append(index)
            self._button_text[index] = []
            if attrs.get("aria-controls"):
                self.anchor_controls.append(attrs)
        if tag == "label" and attrs.get("for"):
            self.labels.add(attrs["for"])
        if tag in {"input", "select", "textarea"}:
            self.controls.append((tag, attrs))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag == "button" and self._button_stack:
            self._button_stack.pop()
        if tag in {"ol", "ul"} and self._list_depth:
            self._list_depth -= 1
        if tag == "pre" and self._pre_depth:
            self._pre_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._list_depth and "```" in data:
            self.fence_in_list = True
        if self._button_stack and data.strip():
            self._button_text[self._button_stack[-1]].append(data.strip())

    def button_name(self, index: int) -> str:
        attrs = self.buttons[index]
        return (
            attrs.get("aria-label")
            or attrs.get("title")
            or " ".join(self._button_text.get(index, []))
        ).strip()


def is_post_route(relative: str) -> bool:
    parts = Path(relative).parts
    return len(parts) >= 4 and parts[0].isdigit()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, default=ROOT)
    args = parser.parse_args()
    site = args.site.resolve()
    if not site.is_dir():
        print(f"site directory does not exist: {site}", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []
    pages = sorted(site.rglob("*.html"))
    if not pages:
        print("no generated HTML pages found", file=sys.stderr)
        return 2

    for path in pages:
        relative = path.relative_to(site).as_posix()
        parser = PageParser()
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except FileNotFoundError:
            errors.append(f"{relative}: generated file disappeared during review")
            continue
        parser.feed(content)

        if not parser.lang:
            errors.append(f"{relative}: html element has no lang")
        if parser.main_ids.count("main-content") != 1:
            errors.append(f"{relative}: expected exactly one #main-content landmark")
        if parser.h1 == 0:
            errors.append(f"{relative}: page has no h1")
        elif parser.h1 > 1:
            warnings.append(f"{relative}: {parser.h1} h1 elements (historical heading review)")
        duplicates = [value for value, count in Counter(parser.ids).items() if count > 1]
        if duplicates:
            warnings.append(f"{relative}: duplicate non-code ids: {duplicates[:4]}")
        if len(parser.aria_current) > 1:
            errors.append(f"{relative}: multiple aria-current links: {parser.aria_current}")

        for index, button in enumerate(parser.buttons):
            if not parser.button_name(index):
                errors.append(f"{relative}: button has no accessible name: {button}")
            if button.get("aria-controls") and not button.get("aria-expanded"):
                warnings.append(f"{relative}: controlled button has no aria-expanded: {button}")

        for tag, control in parser.controls:
            if control.get("type") == "hidden":
                continue
            if control.get("class", "").find("task-list-item-checkbox") >= 0:
                continue
            control_id = control.get("id", "")
            named = (
                control.get("aria-label")
                or control.get("aria-labelledby")
                or control_id in parser.labels
            )
            if not named:
                errors.append(f"{relative}: {tag} control has no label: {control}")

        for link in parser.links:
            rel = set((link.get("rel") or "").split())
            if link.get("target") == "_blank" and "noopener" not in rel:
                errors.append(f"{relative}: target=_blank without noopener: {link.get('href')}")
        if parser.empty_anchors:
            errors.append(f"{relative}: empty anchor href ({len(parser.empty_anchors)})")
        if parser.invalid_hrefs:
            errors.append(f"{relative}: href contains literal whitespace: {parser.invalid_hrefs[:3]}")
        if parser.fence_in_list:
            message = f"{relative}: Markdown fence marker rendered inside a list"
            if relative in KNOWN_HISTORICAL_FENCE_ROUTES:
                warnings.append(message + " (allowlisted historical source; review before migration)")
            else:
                errors.append(message)

    def html(relative: str) -> str:
        return (site / relative).read_text(encoding="utf-8", errors="replace")

    shell_expectations = {
        "index.html": ["id=\"headerMenu\"", "aria-controls=\"headerNav\"", "id=\"themeToggle\""],
        "start-here/index.html": ["domain-map-title", "id=\"path-backend\""],
        "curated/index.html": ["editorial-legend", "path-backend"],
        "category/index.html": ["topic-directory-grid", "topic-anchor-systems"],
        "tag/index.html": ["tag-filter-input", "tag-sort"],
        "search/index.html": ["id=\"search-input\"", "value=\"note\"", "value=\"unknown\""],
        "archive/index.html": ["data-archive-toggle", "aria-controls=\"archive-list-"],
        "about/index.html": ["Systems · C++ · AI infrastructure"],
    }
    for relative, needles in shell_expectations.items():
        content = html(relative)
        for needle in needles:
            if needle not in content:
                errors.append(f"{relative}: missing review marker {needle!r}")

    page2 = html("page2/index.html")
    if not re.search(r'class="active" href="/[^"]*"', page2):
        errors.append("page2/index.html: paginated Home context is not visibly active")

    post_files = [p for p in pages if is_post_route(p.relative_to(site).as_posix())]
    if post_files:
        sample = post_files[0]
        content = sample.read_text(encoding="utf-8", errors="replace")
        if 'class="anchor"' in content and 'aria-controls="post-sidebar"' not in content:
            errors.append(f"{sample.relative_to(site)}: post anchor lacks sidebar control")

    print(f"Reviewed {len(pages)} generated HTML pages")
    print(f"Checks: landmarks, headings, controls, labels, current state, target=_blank, shell markers")
    if warnings:
        print(f"Warnings: {len(warnings)}")
        for warning in warnings[:20]:
            print(f"  ! {warning}")
    if errors:
        print(f"Errors: {len(errors)}")
        for error in errors[:50]:
            print(f"  ✗ {error}")
        return 1
    print("Site review: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

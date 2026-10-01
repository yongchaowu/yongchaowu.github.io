#!/usr/bin/env python3
"""
Generate _data/post_meta.yml: per-post language and reading statistics.

Why this exists
---------------
Three problems needed data that pure Liquid cannot compute, and GitHub Pages
runs Jekyll in safe mode so custom Liquid filters and hooks do not execute
there. So the values are computed here, committed as a data sidecar, and read
back with an O(1) hash lookup in the templates.

1. Language. `_config.yml` sets `lang: en`, but only 71 of 357 posts declare
   `lang` in their front matter, and 267 of the undeclared ones contain CJK
   text. Every one of those was therefore emitting `<html lang="en">`,
   `og:locale="en"` and JSON-LD `"inLanguage": "en"` while displaying Chinese.
   Historical post files must not be rewritten, so the declaration cannot live
   in their front matter -- it lives here instead.

2. Reading time. The layout used to divide a single character count by 800.
   That is right for Chinese (800 chars/min) but roughly 4x too slow for Latin
   script (English runs nearer 200 wpm), so every English post was overstated,
   and the hardcoded "字" unit was shown on all of them.

3. A regression gate. Because the file is committed, `--check` can fail the
   build when a post is added or edited without regenerating, which is what
   stops the two problems above from silently returning.

Matching a post to its record uses the repository-relative `_posts/...` path,
the same key the editorial sidecar uses.

Usage
-----
    uv run --with-requirements scripts/requirements.txt scripts/generate_post_meta.py
    uv run --with-requirements scripts/requirements.txt scripts/generate_post_meta.py --check
"""
import argparse
import json
import os
import re
import sys
from collections import Counter

try:
    import yaml
except ModuleNotFoundError:
    print(
        "PyYAML is required. Run this script with: "
        "uv run --with-requirements scripts/requirements.txt scripts/generate_post_meta.py",
        file=sys.stderr,
    )
    sys.exit(2)

POSTS_DIR = "_posts"
OUTPUT_FILE = os.path.join("_data", "post_meta.yml")
FORMAT_FIXES_FILE = os.path.join("_data", "format_fixes.yml")

# CJK signal. Ideographs plus Extension A, kana, and fullwidth forms: enough to
# decide a language without pulling in a Unicode table dependency.
CJK_RANGES = (
    "一-鿿"      # CJK Unified Ideographs
    "㐀-䶿"      # Extension A
    "぀-ヿ"      # Hiragana + Katakana
    "가-힯"      # Hangul syllables
    "　-〿"      # CJK symbols and punctuation
    "＀-￯"      # Fullwidth forms
)
CJK_RE = re.compile("[" + CJK_RANGES + "]")

# Reading rates. Chinese technical prose with embedded English terms sits around
# 500-800 chars/min; 800 was the original divisor and is kept for CJK. English
# technical prose sits around 200-250 wpm.
CJK_CHARS_PER_MINUTE = 800
LATIN_WORDS_PER_MINUTE = 220

# Language classification.
#
# The first version of this used a flat "20 CJK characters" threshold. Measured
# against the corpus it was a poor discriminator in both directions:
# `2023-02-28-正则表达式-常用正则表达式.md` is 7 CJK characters and 0 Latin words --
# entirely Chinese prose wrapped around a code block -- and was called `en`, while
# `2020-09-30-Code-C++-Get-local-IP.md` is 20 CJK and 20 Latin words and was called
# `zh-CN`. A flat count cannot see the ratio.
#
# So: CJK characters are compared against Latin words, which is a rough parity
# proxy (one English word carries roughly the information of one to two Chinese
# characters), with absolute floors at both ends so a single borrowed word in an
# English article cannot flip it and a handful of characters in a code-heavy post
# cannot either. Posts that land near the boundary are marked low confidence and
# smoke-test.rb refuses to let an outright inversion through.
CJK_MIN_CHARS = 10      # below this the CJK count is noise
LATIN_MIN_WORDS = 40    # above this the post is English with a borrowed term

# Stripped before counting, so that fenced code, inline code, link targets and
# image syntax do not inflate the statistics.
FRONT_MATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---", re.S)
FENCED_CODE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`]*`")
MARKDOWN_LINK_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
HTML_TAG_RE = re.compile(r"<[^>]+>")

LATIN_WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9''\-\.]*")


def split_front_matter(text):
    """Return (front_matter_text, body_text). Front matter is '' when absent."""
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return "", text
    return match.group(1), text[match.end():]


def readable_text(body):
    """Reduce a Markdown body to the prose a reader actually reads.

    The whole body is measured, not the part before `<!--more-->`. Several posts
    put that marker on the first body line, so excerpting first would have
    produced the same empty statistics that emptied the RSS descriptions.
    """
    text = FENCED_CODE_RE.sub(" ", body)
    text = INLINE_CODE_RE.sub(" ", text)
    text = MARKDOWN_LINK_RE.sub(r"\1", text)
    text = HTML_TAG_RE.sub(" ", text)
    # Heading markers, list bullets, blockquote and table pipes.
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"^\s{0,3}[-*+]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s{0,3}>\s?", "", text, flags=re.M)
    text = text.replace("|", " ")
    return text


def measure(body):
    """Return per-script counts and the reading estimate in minutes.

    The count and its unit follow the article's language, because that is what a
    reader expects to see ("N 字" for Chinese, "N words" for English). The
    estimate is the larger of the two per-script figures, so the embedded English
    inside a Chinese article is not silently ignored and vice versa.
    """
    text = readable_text(body)
    cjk_chars = len(CJK_RE.findall(text))
    latin_words = len(LATIN_WORD_RE.findall(text))
    cjk_minutes = cjk_chars / float(CJK_CHARS_PER_MINUTE)
    latin_minutes = latin_words / float(LATIN_WORDS_PER_MINUTE)
    return {
        "first_prose": re.sub(r"\s+", " ", text).strip()[:200],
        "cjk_chars": cjk_chars,
        "latin_words": latin_words,
        "cjk_minutes": cjk_minutes,
        "latin_minutes": latin_minutes,
    }


def load_correction_dates():
    """Map post path -> date of its most recent recorded correction.

    Read from _data/format_fixes.yml rather than invented, because a "last
    reviewed" date that nobody can trace is worse than no date at all. That file
    is the audit trail of deliberate changes to preserved posts, so its latest
    date is a defensible lower bound on when the article was last looked at
    critically.
    """
    dates = {}
    if not os.path.isfile(FORMAT_FIXES_FILE):
        return dates
    with open(FORMAT_FIXES_FILE, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    for entry in data.get("fixes") or []:
        if not isinstance(entry, dict):
            continue
        path = entry.get("post")
        when = entry.get("date")
        if not path or not when:
            continue
        when = str(when)
        if path not in dates or when > dates[path]:
            dates[path] = when
    return dates


def collect_posts(posts_dir):
    """Build {repo_relative_path: record} for every published post."""
    records = {}
    problems = []
    corrections = load_correction_dates()
    if not os.path.isdir(posts_dir):
        print(f"error: {posts_dir}/ not found; run from the repository root",
              file=sys.stderr)
        sys.exit(2)
    for name in sorted(os.listdir(posts_dir)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(posts_dir, name)
        with open(path, "r", encoding="utf-8") as handle:
            text = handle.read()
        fm_text, body = split_front_matter(text)
        try:
            front = yaml.safe_load(fm_text) or {}
        except yaml.YAMLError as exc:
            problems.append(f"{path}: unparseable front matter: {exc}")
            continue
        if not isinstance(front, dict):
            problems.append(f"{path}: front matter is not a mapping")
            continue

        stats = measure(body)
        declared = front.get("lang")
        declared = str(declared) if declared else ""
        cjk, words = stats["cjk_chars"], stats["latin_words"]
        if declared:
            lang, source, confidence = declared, "declared", "high"
        elif cjk == 0:
            lang, source, confidence = "en", "inferred", "high"
        elif cjk < CJK_MIN_CHARS and words < LATIN_MIN_WORDS:
            # Too little of either script to call it. The corpus is majority
            # Chinese, so that is the default, but it is a guess.
            lang, source, confidence = "zh-CN", "inferred", "low"
        elif words >= LATIN_MIN_WORDS and cjk < CJK_MIN_CHARS:
            lang, source, confidence = "en", "inferred", "high"
        elif cjk >= words:
            lang, source, confidence = "zh-CN", "inferred", "high"
        else:
            lang, source, confidence = "en", "inferred", "high"

        # Unit and displayed count follow the language; the estimate is the
        # larger of the two per-script figures so neither script is ignored.
        minutes = max(1, int(round(max(stats["cjk_minutes"], stats["latin_minutes"]))))
        if lang.startswith("zh"):
            count, unit = stats["cjk_chars"], "chars"
        else:
            count, unit = stats["latin_words"], "words"

        # "Last reviewed" is the strongest evidence available, in order: an
        # explicit `updated` in front matter, then the date of the most recent
        # recorded correction. No field is invented when neither exists.
        reviewed = front.get("updated")
        reviewed = str(reviewed)[:10] if reviewed else corrections.get("_posts/" + name, "")

        # Card and search-index text. `post.summary` is preferred by the
        # templates, but 7 posts declare none and their excerpt is empty because
        # `<!--more-->` sits on the first body line, so every card and every
        # search entry for them rendered blank. The first slice of readable prose
        # is the honest last resort: it is a real sentence from the article, not
        # a generated description.
        front_summary = front.get("summary")
        front_summary = re.sub(r"\s+", " ", str(front_summary)).strip() if front_summary else ""
        card_text = front_summary or stats["first_prose"]

        key = "_posts/" + name
        records[key] = {
            "card_summary": card_text,
            "lang": lang,
            "lang_source": source,
            "lang_confidence": confidence,
            "reviewed": reviewed,
            "cjk_chars": stats["cjk_chars"],
            "latin_words": stats["latin_words"],
            "count": count,
            "reading_unit": unit,
            "reading_minutes": minutes,
        }
    return records, problems


def render(records):
    """Serialise deterministically: no timestamps, sorted keys."""
    lines = [
        "# Generated by scripts/generate_post_meta.py -- do not edit by hand.",
        "# Run: uv run --with-requirements scripts/requirements.txt \\",
        "#        scripts/generate_post_meta.py",
        "# Verify: add --check",
        "#",
        "# `lang` is the front-matter value when the post declares one, otherwise",
        "# inferred from the CJK character count of its prose. `reading_minutes`",
        "# is estimated per script: CJK at %d chars/min, Latin at %d words/min."
        % (CJK_CHARS_PER_MINUTE, LATIN_WORDS_PER_MINUTE),
        "version: 1",
        "posts:",
    ]
    for key in sorted(records):
        rec = records[key]
        lines.append(f"  {key}:")
        for field in ("card_summary", "lang", "lang_source", "lang_confidence",
                      "reviewed", "cjk_chars", "latin_words", "count",
                      "reading_unit", "reading_minutes"):
            value = rec[field]
            if isinstance(value, int):
                rendered = str(value)
            else:
                # json.dumps gives a valid double-quoted YAML scalar. yaml.safe_dump
                # would append a "...\n" document-end marker and corrupt the file.
                rendered = json.dumps(value, ensure_ascii=False)
            lines.append(f"    {field}: {rendered}")
    return "\n".join(lines) + "\n"


def summarise(records):
    langs = Counter(r["lang"] for r in records.values())
    sources = Counter(r["lang_source"] for r in records.values())
    units = Counter(r["reading_unit"] for r in records.values())
    reviewed = sum(1 for r in records.values() if r.get("reviewed"))
    low = sum(1 for r in records.values() if r.get("lang_confidence") == "low")
    blank = sum(1 for r in records.values() if not r.get("card_summary"))
    print(f"Posts: {len(records)}")
    print("Language: " + ", ".join(f"{k}={v}" for k, v in sorted(langs.items())))
    print("Source:   " + ", ".join(f"{k}={v}" for k, v in sorted(sources.items())))
    print("Unit:     " + ", ".join(f"{k}={v}" for k, v in sorted(units.items())))
    print(f"Reviewed: {reviewed} of {len(records)} posts carry a traceable date")
    print(f"Low-confidence language: {low} (too little prose of either script to call)")
    print(f"Card summary available: {len(records) - blank}/{len(records)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true",
                        help="verify the committed file matches the posts; write nothing")
    args = parser.parse_args()

    records, problems = collect_posts(POSTS_DIR)
    if problems:
        print("Post front matter errors:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1
    if not records:
        print(f"error: no posts found under {POSTS_DIR}/", file=sys.stderr)
        return 1

    expected = render(records)

    if args.check:
        if not os.path.exists(OUTPUT_FILE):
            print(f"FAIL: {OUTPUT_FILE} does not exist; run without --check",
                  file=sys.stderr)
            return 1
        with open(OUTPUT_FILE, "r", encoding="utf-8") as handle:
            actual = handle.read()
        if actual != expected:
            print(f"FAIL: {OUTPUT_FILE} is stale; run "
                  f"scripts/generate_post_meta.py without --check", file=sys.stderr)
            print("  posts with generated data: " + str(len(records)), file=sys.stderr)
            return 1
        summarise(records)
        print(f"Post metadata consistency: PASS ({len(records)} posts)")
        return 0

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as handle:
        handle.write(expected)
    summarise(records)
    print(f"Wrote {OUTPUT_FILE} ({len(records)} posts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

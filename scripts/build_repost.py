#!/usr/bin/env python3
"""Build the cnblogs re-publication set from this repository's corrected versions.

Why this exists
---------------
Six articles here are factually better than their cnblogs counterparts, and one
more is worse there than here in a way that breaks the reader:

  New-API-Multi-Process-Docker      cnblogs still documents the withdrawn
                                    built-in-Worker design and never names the
                                    official calciumion/new-api image, so a
                                    reader following it deploys something that
                                    does not work.
  Script-managing-screen-timeout    cnblogs still has `grep -oP '\\d+'`, which
                                    has no end anchor and matches the digits in
                                    "123abc".
  Code-C++-regex                    cnblogs has the article reduced to 101
                                    characters of syntactically invalid C++.
  VitePress-Complete-Guide          cnblogs' alpha.20 examples do not match the
                                    prerelease channel and it omits the
                                    site-level appearance and lazyLoad options.
  BehaviorTree.CPP_v4.9             cnblogs states the SequentialNode parallel
                                    condition without the ThreadedAction
                                    exception.
  Multi-Node-LLM-Serving-Architecture  cnblogs has wrong token arithmetic and
                                    presents unverified HPA metrics as fact.
  kylin-v10-sp1 / linux-usb-log-cleaner / gh-api-disable-actions
                                    these carry body-level H1 headings on a page
                                    whose title is already an H1, on both
                                    platforms. Presentational rather than
                                    factual, included because the fix is trivial
                                    and the pages are wrong either way.

Base is this repository's version, not upstream's, because that is where the
corrections are. What has to go is everything Jekyll-specific, and this is the
part that needs care:

  `{% raw %}` wrappers       Pure Jekyll. cnblogs is not Liquid, and keeping them
                             would render the wrapper text verbatim.
  `{% post_url X %}`         A Jekyll filter that resolves a slug to a URL. On
                             cnblogs it would be literal text, so the link text
                             is kept and the tag dropped.
  `<!--more-->`              This site's excerpt separator. cnblogs has its own
                             mechanism; a literal marker would be visible.

The output keeps only the front matter cnblogs understands, so the files are
readable on their own and can be pasted into the editor.

Usage: python3 scripts/build_repost.py [--out DIR] [--dry-run]
"""
import argparse
import os
import re
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.expanduser(
    "~/Workspace/Blog/cnblogs_blog_yongchao.20261001000949/yongchao")

# Front matter cnblogs understands. Everything else -- layout, display_title,
# lang, categories, upstream_sync, upstream_sync_reason, source_posts -- is a
# Jekyll-side concern and would either be ignored or confuse the editor.
KEEP_FM = {"title", "date", "tags", "categories", "original", "link"}

# post: (upstream export filename stem, why it is in the set)
REPOST = {
    "2026-09-05-New-API-Multi-Process-Docker.md": (
        "cnblogs still documents the withdrawn built-in-Worker design and never "
        "names the official calciumion/new-api image; a reader following it "
        "deploys something that does not work."),
    "2026-06-04-Script-managing-screen-timeout-and-power-mode-settings-on-linux.md": (
        "cnblogs still has grep -oP '\\d+' with no end anchor, which matches the "
        "digits in a value like 123abc."),
    "2024-08-15-Code-C++-regex.md": (
        "cnblogs has this reduced to 101 characters and the first line is not a "
        "valid C++ statement -- it has no declarator."),
    "2026-09-05-VitePress-Complete-Guide.md": (
        "cnblogs' alpha.20 examples do not match the prerelease channel, and it "
        "omits the site-level appearance option, the lazyLoad image option and "
        "the version warning."),
    "2026-07-15-OpenSource-BehaviorTree.CPP_v4.9_Complete_Guide(LLM-Generated).md": (
        "cnblogs states the SequentialNode parallel condition without the "
        "documented ThreadedAction exception."),
    "2026-06-12-Multi-Node-LLM-Serving-Architecture,-Frameworks-and-Best-Practices-(LLM-Generated).md": (
        "cnblogs has wrong token arithmetic and presents unverified performance "
        "and location HPA metrics as fact."),
    "2026-09-08-kylin-v10-sp1-offline-cpp-development-environment.md": (
        "presentational: cnblogs carries 15 body-level H1 headings on a page "
        "whose title is already an H1."),
    "2026-09-10-linux-usb-log-cleaner-blog-v2.2.md": (
        "presentational: 68 body-level H1 headings on cnblogs against 43 here."),
    "2026-09-27-gh-api-disable-actions-all-forks.md": (
        "presentational: 26 body-level H1 headings on cnblogs against 23 here."),
}

FM_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.S)
FENCE_SPLIT_RE = re.compile(r"(^[ \t]*`{3,}[^\n]*$.*?^[ \t]*`{3,}[^\n]*$)", re.S | re.M)
RAW_RE = re.compile(r"{%-?\s*raw\s*-?%}(.*?){%-?\s*endraw\s*-?%}", re.S)
POST_URL_RE = re.compile(r"{%-?\s*post_url\s+[^%]*?-?%}")
MORE_RE = re.compile(r"[ \t]*<!--\s*more\s*-->[ \t]*\n?")
# An H1 that is not the article title: the page title is already an H1.
BODY_H1_RE = re.compile(r"(?m)^#(?!#)(?![ \t]*$)(.*?)[ \t]*$")


def strip_jekyll(body):
    """Remove the constructs that only mean something to Jekyll.

    Two passes, in this order, and the order is the whole point.

    Pass one runs over the whole text and removes the raw/post_url/excerpt tags.
    These are tag-only deletions -- the payload between `{% raw %}` and
    `{% endraw %}` is kept verbatim -- so they cannot alter code. They do have to
    run unsplit: on 2026-09-05-New-API-Multi-Process-Docker the opening
    `{% raw %}` sits in the prose before the first fence and the matching
    `{% endraw %}` in the prose after it, so a fence-aware pass that requires both
    ends in the same segment pairs neither of them and leaves both in the output.

    Pass two is fence-aware and does only the H1 demotion, which does rewrite
    content. It must be fence-aware: on
    2026-09-10-linux-usb-log-cleaner-blog-v2.2.md an entire bash script is
    embedded, and every one of its comments starts with `#`, so a whole-file
    regex turned the comments into `## ` and the shebang into
    `##!/usr/bin/env bash`.
    """
    body = RAW_RE.sub(r"\1", body)        # keep the payload, drop the guard
    body = POST_URL_RE.sub("", body)      # keep the link text
    body = MORE_RE.sub("", body)          # drop the excerpt marker

    parts = FENCE_SPLIT_RE.split(body)
    for i, part in enumerate(parts):
        if i % 2 == 1:            # inside a fence: the code is content
            continue
        parts[i] = BODY_H1_RE.sub(lambda m: "## " + m.group(1), part)
    body = "".join(parts)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip()


def prose_only(text):
    """Yield the parts of `text` that are outside fenced code blocks."""
    for i, part in enumerate(FENCE_SPLIT_RE.split(text)):
        if i % 2 == 0:
            yield part


def body_h1_outside_fences(text):
    """True if any prose H1 survived the demotion.

    The fence exclusion is not a detail. New-API carries a docker-compose file
    and a long shell session whose comments all begin with `#`; a plain
    `^#(?!#)` scan reported 80 body-level H1s on that article and called the
    conversion broken, when every one of them was a `# 1. 安装 NVIDIA 驱动`
    comment inside a fence. The check would have rejected correct output.
    """
    return any(re.search(r"(?m)^#(?!#)", part) for part in prose_only(text))


def fenced_blocks(text):
    """Yield the contents of every fenced code block, for verification."""
    for i, part in enumerate(FENCE_SPLIT_RE.split(text)):
        if i % 2 == 1:
            inner = re.sub(r"^[ \t]*`{3,}[^\n]*\n?", "", part)
            inner = re.sub(r"\n?[ \t]*`{3,}[ \t]*$", "", inner)
            yield inner


def keep_front_matter(fm_text):
    """Return only the fields cnblogs understands.

    Parsed with a YAML library rather than by scanning lines. The line-based
    version appended the continuation lines of a dropped field to whatever field
    preceded it, so `upstream_sync_reason` -- a folded block scalar -- landed
    inside the `tags` list and produced front matter that is not valid YAML at
    all. A file that fails to import is worse than one that carries a field
    nobody asked for.

    `original` and `link` are kept because cnblogs writes them itself, so a
    round trip through the editor does not lose them.
    """
    import yaml
    try:
        data = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as exc:
        raise SystemExit(f"cannot parse front matter: {exc}")
    if not isinstance(data, dict):
        return ""
    kept = {k: v for k, v in data.items() if k in KEEP_FM and v not in (None, "", [])}
    if not kept:
        return ""
    return yaml.safe_dump(kept, allow_unicode=True, sort_keys=False,
                          default_flow_style=False).strip()


def export_name_for(post_name):
    """Find the cnblogs export file this post came from, by normalized name."""
    norm = re.sub(r"[^0-9a-z\u3400-\u9fff]+", "",
                  post_name.replace("&", " and ").lower())
    for name in sorted(os.listdir(EXPORT_DIR)):
        stem = re.sub(r"\.\d{5,}$", "", name[:-3])
        if re.sub(r"[^0-9a-z\u3400-\u9fff]+", "",
                  stem.replace("&amp;", "&").replace("&", " and ").lower()) == norm:
            return name
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.expanduser("~/Workspace/Blog/repost"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    missing = [p for p in REPOST if not os.path.isfile(os.path.join("_posts", p))]
    if missing:
        print("error: posts not found:", *missing, sep="\n  ", file=sys.stderr)
        return 2

    os.makedirs(args.out, exist_ok=True)
    print("=" * 72)
    print("Re-publication set for cnblogs" + ("  [DRY RUN]" if args.dry_run else ""))
    print("=" * 72)
    print(f"  output  {args.out}")
    print(f"  posts   {len(REPOST)}\n")

    for post, why in REPOST.items():
        raw = open(os.path.join("_posts", post), encoding="utf-8").read()
        m = FM_RE.match(raw)
        fm = keep_front_matter(m.group(1)) if m else ""
        body = strip_jekyll(raw[m.end():] if m else raw)

        export = export_name_for(post)
        out_name = (export[:-3] + ".md") if export else post
        target = os.path.join(args.out, out_name)

        # Sanity: a re-published file must not contain Jekyll-only syntax.
        problems = []
        if RAW_RE.search(body):
            problems.append("raw wrapper survived")
        if POST_URL_RE.search(body):
            problems.append("post_url survived")
        if "<!--more-->" in body:
            problems.append("excerpt marker survived")
        if body_h1_outside_fences(body):
            problems.append("body-level H1 present")
        # The strongest available guarantee: every fenced block in the output is
        # byte-identical to the corresponding block in the source. This is what
        # catches a demotion or a strip that reached inside a code sample.
        src_blocks = list(fenced_blocks(raw[m.end():] if m else raw))
        out_blocks = list(fenced_blocks(body))
        if len(src_blocks) != len(out_blocks):
            problems.append(f"code block count {len(src_blocks)} -> {len(out_blocks)}")
        else:
            for i, (a, b) in enumerate(zip(src_blocks, out_blocks)):
                if a != b:
                    problems.append(f"code block {i} was modified")
                    break
        if not body.strip():
            problems.append("empty body")
        if problems:
            print(f"  !! {post}\n       {', '.join(problems)}")
            return 1

        text = f"---\n{fm}\n---\n\n{body}\n"
        if not args.dry_run:
            with open(target, "w", encoding="utf-8") as fh:
                fh.write(text)
        h1 = len(re.findall(r"(?m)^## ", body))
        print(f"  {post[:58]:58s}")
        print(f"      -> {out_name[:58]}")
        print(f"      {len(body):6d} chars, {len(body.splitlines()):4d} lines, "
              f"{h1} H2, front matter: {fm.splitlines()[0] if fm else '(none)'}")
        print(f"      why: {why[:96]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

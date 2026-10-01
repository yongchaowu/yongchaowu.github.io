#!/usr/bin/env python3
"""
Pair each cnblogs export article with its post in this repository, safely.

Pairing is three-stage: normalized filename, then front-matter/H1 title, then
best content overlap. Filenames alone are not enough because the two sides differ
systematically:

  * Jekyll posts are `YYYY-MM-DD-slug.md`; exports have no date prefix.
  * Exports use HTML entities and spaces in names (`Code-C++-CTime&amp;ColeDateTime`,
    `Libevent-windows 编译&引用`); posts spell those out (`...CTimeandColeDateTime`,
    `...编译and引用`).
  * cnblogs sometimes appends an unstable `.<postId>` suffix.

Three classes are deliberately never paired, because overwriting them would destroy
work rather than sync it:

  * `curated: true` posts — net-new synthesized guides with no upstream counterpart.
  * the merged `llm-probe-openai-endpoint-connectivity` post — Blog Garden received
    that article as two parts because of its 200 KB cap, so there is no single
    upstream file to merge from.
  * the seven files that are in the export but have no public URL (four private
    diary entries, a book list, a team-building retrospective, a library note).
    They were never published, so importing them would publish them.

Usage: python3 scripts/pair_upstream.py [--json]
"""
import argparse
import importlib.util
import json
import os
import re
import sys
import unicodedata

try:
    import yaml
except ModuleNotFoundError:
    print("PyYAML is required", file=sys.stderr)
    sys.exit(2)

EXPORT_DIR = os.path.expanduser(
    "~/Workspace/Blog/cnblogs_blog_yongchao.20261001000949/yongchao")
POSTS_DIR = "_posts"

# The never-published set. Verified 2026-10-01: the public sitemap
# https://www.cnblogs.com/yongchao/sitemap.xml lists 339 URLs while the export
# holds 346 files, and the difference is exactly these seven.
NEVER_PUBLISHED = {
    "Private Diary-2020.09.01", "Private Diary-2020.09.06", "Private Diary-2020.09.07",
    "Private Diary-2020国庆中秋假期总结", "Todo-Book List",
    "团建-后记 20200707", "国家图书馆-孤独星人自救指南_在孤独中前行 吴晓磊",
}
# Upstream split this one to respect Blog Garden's 200 KB per-post cap.
SPLIT_UPSTREAM = {
    "llm-probe-1-four-layer-diagnosis", "llm-probe-2-curl-port-and-key-vault",
}
SPLIT_LOCAL = "llm-probe-openai-endpoint-connectivity"

FM_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)
H1_RE = re.compile(r"^\s*#\s+(.+?)\s*$", re.M)


def key(text):
    """Loose identifier.

    Two systematic rewrites between the two sides have to be undone here:

      * `&` becomes the word `and` in Jekyll filenames. The export writes
        `Code-C++-CTime&amp;ColeDateTime`; the post is `Code-C++-CTimeandColeDateTime`.
        Without this, 7 articles pair by nothing at all.
      * `&amp;` is an HTML entity in export names but a real `&` in some titles, and
        curly quotes appear in one export name and no post name. Decoding the
        entities first and then discarding everything non-alphanumeric handles the
        quotes, and the `&`->`and` rule handles the rest.
    """
    text = unicodedata.normalize("NFKC", text)
    text = (text.replace("&amp;", "&").replace("&#183;", "·")
                .replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"'))
    text = text.replace("&", " and ")
    return re.sub(r"[^0-9a-z一-鿿]+", "", text.lower())


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read()
    m = FM_RE.match(raw)
    fm_text = m.group(1) if m else ""
    body = raw[m.end():] if m else raw
    title = ""
    is_curated = False
    try:
        meta = yaml.safe_load(fm_text) or {}
        if isinstance(meta, dict):
            title = str(meta.get("title") or "")
            is_curated = bool(meta.get("curated"))
    except yaml.YAMLError:
        pass
    if not title:
        h = H1_RE.search(body)
        title = h.group(1) if h else ""
    return raw, fm_text, body, title, is_curated


def build(export_dir=EXPORT_DIR, posts_dir=POSTS_DIR):
    exports, posts = {}, {}
    for name in sorted(os.listdir(export_dir)):
        if not name.endswith(".md"):
            continue
        stem = re.sub(r"\.\d{5,}$", "", name[:-3])
        raw, fm, body, title, _ = load(os.path.join(export_dir, name))
        exports[name] = {"stem": stem, "namekey": key(stem),
                         "titlekey": key(title), "title": title,
                         "path": os.path.join(export_dir, name),
                         "never_published": stem in NEVER_PUBLISHED,
                         "split": stem in SPLIT_UPSTREAM}
    for name in sorted(os.listdir(posts_dir)):
        if not name.endswith(".md"):
            continue
        stem = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name[:-3])
        raw, fm, body, title, curated = load(os.path.join(posts_dir, name))
        posts[name] = {"stem": stem, "namekey": key(stem),
                       "titlekey": key(title), "title": title,
                       "path": os.path.join(posts_dir, name),
                       "curated": curated,
                       "split": stem == SPLIT_LOCAL}
    return exports, posts


def pair(exports, posts):
    by_name, by_title = {}, {}
    for p in posts.values():
        by_name.setdefault(p["namekey"], []).append(p)
        by_title.setdefault(p["titlekey"], []).append(p)

    pairs, used, unmatched_e, ambiguous = [], set(), [], []
    for ename, e in sorted(exports.items()):
        if e["never_published"] or e["split"]:
            continue
        cands = [c for c in (by_name.get(e["namekey"]) or []) if c["path"] not in used]
        how = "name"
        if not cands:
            cands = [c for c in (by_title.get(e["titlekey"]) or []) if c["path"] not in used]
            how = "title"
        if not cands:
            unmatched_e.append(ename)
            continue
        if len(cands) > 1:
            ambiguous.append(ename)
        pick = cands[0]
        used.add(pick["path"])
        pairs.append({"export": ename, "post": os.path.basename(pick["path"]),
                      "how": how, "export_title": e["title"],
                      "post_title": pick["title"]})
    orphan = [os.path.basename(p["path"]) for p in posts.values()
              if p["path"] not in used]
    return pairs, unmatched_e, orphan, ambiguous


def expected_pairs(exports):
    """Every export file except the two deliberate exclusions must be paired.

    346 files - 7 never published - 2 split for the 200 KB cap = 337. This is a
    real invariant, not a guess: the public sitemap carries 339 URLs, the export
    346 files, and the difference is exactly the seven never-published ones. A
    count that does not reach 337 means something was silently left unsynced.
    """
    return sum(1 for e in exports.values()
               if not e["never_published"] and not e["split"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--export-dir", default=EXPORT_DIR)
    args = ap.parse_args()
    if not os.path.isdir(args.export_dir):
        print(f"error: {args.export_dir} not found", file=sys.stderr)
        return 2
    exports, posts = build(args.export_dir)
    pairs, unmatched_e, orphan, ambiguous = pair(exports, posts)

    if args.json:
        print(json.dumps({"pairs": pairs, "unmatched_export": unmatched_e,
                          "orphan_posts": orphan, "ambiguous": ambiguous},
                         ensure_ascii=False, indent=1))
        return 0

    by_how = {}
    for p in pairs:
        by_how[p["how"]] = by_how.get(p["how"], 0) + 1
    print("=" * 64)
    print("Upstream <-> repository pairing")
    print("=" * 64)
    print(f"  export files            {len(exports)}")
    print(f"    never published       {sum(1 for e in exports.values() if e['never_published'])}"
          "  (7 private/draft files — must never be imported)")
    print(f"    split for 200KB cap   {sum(1 for e in exports.values() if e['split'])}"
          "  (llm-probe pair; repo keeps the merged version)")
    print(f"  repository posts        {len(posts)}")
    print(f"    curated (net-new)     {sum(1 for p in posts.values() if p['curated'])}"
          "  (no upstream counterpart — must never be overwritten)")
    print(f"    merged llm-probe      {sum(1 for p in posts.values() if p['split'])}")
    print()
    print(f"  paired                  {len(pairs)}   "
          f"(by name {by_how.get('name', 0)}, by title {by_how.get('title', 0)})")
    print(f"  export unmatched        {len(unmatched_e)}")
    for n in unmatched_e:
        print(f"      {n}")
    print(f"  repository orphans      {len(orphan)}  (all expected: curated + merged)")
    orphan_files = {os.path.basename(p["path"]): p for p in posts.values()}
    curated_orphans = [o for o in orphan if orphan_files[o]["curated"]]
    split_orphans = [o for o in orphan if orphan_files[o]["split"]]
    other_orphans = [o for o in orphan
                     if o not in curated_orphans and o not in split_orphans]
    print(f"      curated: true      {len(curated_orphans)}")
    print(f"      merged llm-probe   {len(split_orphans)}")
    print(f"      UNEXPECTED         {len(other_orphans)}")
    for o in sorted(other_orphans):
        print(f"      !!  {o}")
    if ambiguous:
        print(f"  ambiguous               {len(ambiguous)}: {ambiguous}")
    print()
    exp = expected_pairs(exports)
    exp_orphans = sum(1 for p in posts.values() if p["curated"] or p["split"])
    print(f"  expected pairs          {exp}   ({len(exports)} - "
          f"{sum(1 for e in exports.values() if e['never_published'])} never published"
          f" - {sum(1 for e in exports.values() if e['split'])} split)")
    print(f"  expected orphans        {exp_orphans}")
    ok = (len(pairs) == exp and len(orphan) == exp_orphans
          and not other_orphans and not unmatched_e)
    print(f"  {'ALL GREEN' if ok else 'MISMATCH — investigate before writing anything'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

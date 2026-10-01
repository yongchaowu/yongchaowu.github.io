#!/usr/bin/env python3
"""
Compare the upstream cnblogs export against this repository's posts.

Why this exists
---------------
cnblogs is the source of truth; this repository is the derived publication
target. The import is deliberately lossy, so a byte or hash comparison is
useless: normalizing whitespace alone reports 356 of 357 posts as "changed".
Verified on 2026-10-01.

The import performs four mechanical transformations that are *not* drift:

  1. Front matter is rewritten. `description` becomes `summary`; `layout`,
     `display_title`, `lang` and `categories` are added; the body H1 is dropped
     because the layout renders the title.
  2. The excerpt separator `<!--more-->` is moved outside any `{% raw %}`
     wrapper.
  3. Code fences and list/HTML structure are repaired where the imported source
     was malformed.
  4. A small number of evidence-backed factual corrections are applied, and each
     one is recorded in _data/format_fixes.yml against an exact resulting blob.

So the useful question is not "do the files match" but "**which differences are
not covered by format_fixes.yml**". Those are the ones that need a human: either
the upstream article was edited after the import and the change never propagated,
or this repository drifted on its own.

Matching is attempted by normalized name, then by title, then by best content
similarity, because a cnblogs export filename and a Jekyll post filename differ
systematically (the Jekyll one carries a `YYYY-MM-DD-` prefix, and cnblogs
sometimes appends an unstable `.<postId>` suffix).

Usage
-----
    python3 scripts/compare_upstream.py [--verbose] [--only SUBSTRING]
"""
import argparse
import difflib
import importlib.util
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

try:
    import yaml
except ModuleNotFoundError:
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

_HERE = os.path.dirname(os.path.abspath(__file__))


def _shared():
    """Import upstream_text.py, which holds the corrections this repo makes.

    Sharing them is what keeps the report honest. Answering "does this post differ
    from upstream" without applying them counted 90 articles as substantive drift
    right after a clean sync, when only 25 were actually awaiting review: the rest
    differed solely by `%20` in a link target, an empty-target link promoted to an
    autolink, or a recorded fix from format_fixes.yml being re-applied.
    """
    spec = importlib.util.spec_from_file_location(
        "upstream_text", os.path.join(_HERE, "upstream_text.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

EXPORT_DIR = os.environ.get(
    "CNBLOGS_EXPORT",
    os.path.expanduser(
        "~/Workspace/Blog/cnblogs_blog_yongchao.20261001000949/yongchao"))
POSTS_DIR = "_posts"
FORMAT_FIXES = os.path.join("_data", "format_fixes.yml")

# The import is lossy by design; these are stripped before comparing bodies.
FM_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)
H1_RE = re.compile(r"^\s*#\s+(.+?)\s*$", re.M)
MORE_RE = re.compile(r"<!--\s*more\s*-->")
CODE_FENCE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
LIQUID_RAW_RE = re.compile(r"\{%-?\s*(raw|endraw)\s*-?%\}")
MD_LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
BARE_URL_RE = re.compile(r"(?<![(\[<])(https?://[^\s<>()\[\]]+)")


def key(text):
    """Loose identifier: NFKC, entities decoded, only letters/digits/CJK."""
    text = unicodedata.normalize("NFKC", text)
    text = (text.replace("&amp;", "&").replace("&#183;", "·")
                .replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"'))
    return re.sub(r"[^0-9a-z一-鿿]+", "", text.lower())


def split_fm(text):
    m = FM_RE.match(text)
    return (m.group(1), text[m.end():]) if m else ("", text)


def read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


# normalize_body, typographic_normalize, is_declaration_only, word_set and
# version_delta now live in upstream_text.py. They used to be defined here and
# were imported from here by the sync script, which meant the report and the
# writer each carried a copy of "what counts as the same text" and drifted apart
# the moment either was edited.
_T = _shared()
# The text-level primitives now live in upstream_text.py; re-exported here so the
# rest of this file reads unchanged and so there is exactly one definition of "the
# same text" across the report and the writer.
normalize_body = _T.normalize_body
typographic_normalize = _T.typographic_normalize
is_declaration_only = _T.is_declaration_only
word_set = _T.word_set
version_delta = _T.version_delta
bodies_equivalent = _T.bodies_equivalent
strip_leading_h1 = _T.strip_leading_h1


def load_format_fixes():
    if not os.path.isfile(FORMAT_FIXES):
        return {}
    with open(FORMAT_FIXES, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    out = {}
    for entry in data.get("fixes") or []:
        if isinstance(entry, dict) and entry.get("post"):
            out[entry["post"]] = entry
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true", help="print the unified diff")
    ap.add_argument("--only", help="only posts whose filename contains this")
    ap.add_argument("--export-dir", default=EXPORT_DIR)
    args = ap.parse_args()

    if not os.path.isdir(args.export_dir):
        print(f"error: export dir not found: {args.export_dir}", file=sys.stderr)
        return 2
    if not os.path.isdir(POSTS_DIR):
        print("error: run from the repository root", file=sys.stderr)
        return 2

    fixes = load_format_fixes()

    # --- load both corpora -------------------------------------------------
    exports = {}
    for name in sorted(os.listdir(args.export_dir)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(args.export_dir, name)
        fm, body = split_fm(read(path))
        title = ""
        try:
            meta = yaml.safe_load(fm) or {}
            if isinstance(meta, dict):
                title = str(meta.get("title") or "")
        except yaml.YAMLError:
            pass
        if not title:
            m = H1_RE.search(body)
            title = m.group(1) if m else name[:-3]
        stem = re.sub(r"\.\d{5,}$", "", name[:-3])       # unstable .<postId>
        exports[name[:-3]] = {
            "file": name, "title": title,
            "body": normalize_body(body, title), "raw": body,
            "namekey": key(stem), "titlekey": key(title),
        }

    posts = {}
    for name in sorted(os.listdir(POSTS_DIR)):
        if not name.endswith(".md"):
            continue
        raw = read(os.path.join(POSTS_DIR, name))
        fm, body = split_fm(raw)
        title = ""
        try:
            meta = yaml.safe_load(fm) or {}
            if isinstance(meta, dict):
                title = str(meta.get("title") or "")
        except yaml.YAMLError:
            pass
        if not title:
            m = H1_RE.search(body)
            title = m.group(1) if m else name[:-3]
        stem = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name[:-3])
        posts[name] = {
            "file": name, "title": title,
            # raw_full carries the front matter too: flow_direction() reads the
            # `upstream_sync` override from it, and split_fm would drop it.
            "body": normalize_body(body, title), "raw": body, "raw_full": raw,
            "namekey": key(stem), "titlekey": key(title),
            "path": "_posts/" + name,
        }

    # --- match ------------------------------------------------------------
    by_name, by_title = {}, {}
    for p in posts.values():
        by_name.setdefault(p["namekey"], []).append(p)
        by_title.setdefault(p["titlekey"], []).append(p)

    pairs, unmatched_posts, ambiguous = [], [], []
    used = set()
    for ename, e in exports.items():
        cands = by_name.get(e["namekey"]) or by_title.get(e["titlekey"]) or []
        cands = [c for c in cands if c["file"] not in used]
        if not cands:
            unmatched_posts.append(ename)
            continue
        if len(cands) > 1:
            # disambiguate by content overlap
            ew = word_set(e["body"])
            cands.sort(key=lambda c: -len(ew & word_set(c["body"])))
            if len(cands) > 1 and \
               len(word_set(cands[0]["body"]) & ew) == len(word_set(cands[1]["body"]) & ew):
                ambiguous.append(ename)
        pick = cands[0]
        used.add(pick["file"])
        pairs.append((e, pick))

    orphan_posts = [p["file"] for p in posts.values() if p["file"] not in used]

    # --- compare ----------------------------------------------------------
    identical, covered, decl, typos, drift = [], [], [], [], []
    corrected_side, held = [], []
    rules = _shared().load_recorded_fixes()
    flow = _shared().flow_direction

    def rules_for(post_path):
        """format_fixes.yml keys are repository-relative; the pairing is not."""
        key = post_path if post_path.startswith("_posts/") else "_posts/" + post_path
        return {key: rules[key]} if key in rules else {}

    for e, p in pairs:
        if args.only and args.only not in p["file"]:
            continue
        if e["body"] == p["body"]:
            identical.append((e, p))
            continue
        # Is this difference already an approved, recorded correction?
        fx = fixes.get(p["path"])
        if fx:
            covered.append((e, p, fx))
            continue
        # Then: rebuild what this repository's copy should be, by exactly the
        # procedure the sync uses, and see whether it already matches. This is the
        # only honest test of "synced" -- comparing the two texts directly cannot
        # see the corrections, and comparing with looser rules than the writer uses
        # overstates the outstanding work.
        want, _notes = _T.expected_body(e["body"], p["body"], rules_for(p["path"]),
                                           p["path"])
        if _T.bodies_equivalent(want, p["body"]):
            corrected_side.append((e, p))
            continue
        if is_declaration_only(e["body"], p["body"]):
            decl.append((e, p))
        elif typographic_normalize(e["body"]) == typographic_normalize(p["body"]):
            typos.append((e, p))
        elif flow(p["file"], p["raw_full"]) == "local":
            # From 2026-06 the flow reverses and is not consistently forward:
            # 14 of the paired posts are behind upstream, 1 is ahead of it, 2 are
            # marked on both sides. Never "drift to fix" -- report for review.
            held.append((e, p))
        else:
            drift.append((e, p))

    # --- report -----------------------------------------------------------
    W = 62
    print("=" * W)
    print("Upstream vs. this repository")
    print("=" * W)
    print(f"  export dir : {args.export_dir}")
    print(f"  export     : {len(exports)} articles")
    print(f"  repository : {len(posts)} posts")
    print(f"  matched    : {len(pairs)}")
    print()
    print("  identical after normalising the import transforms : "
          f"{len(identical)}")
    print("  differ, covered by _data/format_fixes.yml        : "
          f"{len(covered)}")
    print("  differ only by an upstream AI/revision declaration: "
          f"{len(decl)}")
    print("  differ only by CJK/Latin + heading spacing       : "
          f"{len(typos)}")
    print("  synced, differing only by local corrections      : "
          f"{len(corrected_side)}")
    print("  2026-06 and later, held for review (flow reverses): "
          f"{len(held)}")
    print("  differ in substance, NOT recorded <-- review      : "
          f"{len(drift)}")
    print()
    if ambiguous:
        print(f"  ambiguous name matches ({len(ambiguous)}): {ambiguous[:5]}")
        print()
    if unmatched_posts:
        print(f"  in export only, no post here ({len(unmatched_posts)}):")
        for n in unmatched_posts[:20]:
            print(f"      {n}")
        if len(unmatched_posts) > 20:
            print(f"      ... and {len(unmatched_posts) - 20} more")
        print()
    if orphan_posts:
        curated = [f for f in orphan_posts
                   if re.search(r'^_posts/.*curated', f)]
        print(f"  in repository only ({len(orphan_posts)}): "
              f"{len(curated)} curated, {len(orphan_posts) - len(curated)} other")
        for f in sorted(orphan_posts):
            if not re.search(r'curated', f):
                print(f"      {f}")
        print()

    if typos:
        print()
        print("-" * W)
        print("TYPOGRAPHIC ONLY (upstream proofread spacing) -- cosmetic, bulk-fixable")
        print("-" * W)
        print("  Identical apart from spaces between CJK and Latin runs, and the")
        print("  required space after heading markers. Same words, same code, same")
        print("  commands. Safe to normalise in bulk if you want the two domains to")
        print("  read identically.")
        for e, p in sorted(typos, key=lambda x: x[1]["file"]):
            print(f"    {p['file'][:70]}")

    if decl:
        print()
        print("-" * W)
        print("UPSTREAM-ONLY AI / REVISION DECLARATION")
        print("-" * W)
        print("  These articles differ from the source of truth only by a visible")
        print("  modification/revision declaration that the 2026-09-25 upstream")
        print("  proofread pass added. The prose is the same. This is one decision")
        print("  applied across many files, not many separate problems: either the")
        print("  declaration belongs here too, or the two domains are meant to show")
        print("  different text for the same article. Decide once, apply to all.")
        print()
        for e, p in sorted(decl, key=lambda x: x[1]["file"]):
            line = next((l for l in e["raw"].split("\n")
                         if any(mk in l for mk in DECL_MARKERS)), "")
            print(f"    {p['file'][:62]}")
            print(f"        {line.strip()[:96]}")

    if drift:
        print()
        print("-" * W)
        print("UNRECORDED DIFFERENCES")
        print("-" * W)
        for e, p in sorted(drift, key=lambda x: x[1]["file"]):
            ew, pw = word_set(e["body"]), word_set(p["body"])
            only_up = ew - pw
            only_repo = pw - ew
            sim = difflib.SequenceMatcher(None, e["body"], p["body"]).ratio()
            print(f"\n  {p['file']}")
            print(f"    title match : {e['title'][:56]}")
            print(f"    similarity  : {sim:.3f}")
            print(f"    only upstream ({len(only_up)}): "
                  f"{' '.join(sorted(only_up)[:14])}")
            print(f"    only repo    ({len(only_repo)}): "
                  f"{' '.join(sorted(only_repo)[:14])}")
            if args.verbose:
                diff = difflib.unified_diff(
                    e["body"].split("\n"), p["body"].split("\n"),
                    fromfile="cnblogs/" + e["file"], tofile="repo/" + p["file"],
                    lineterm="", n=1)
                for line in list(diff)[:80]:
                    print("      " + line)
    else:
        print("  No unrecorded differences.")

    if covered:
        print()
        print("-" * W)
        print("RECORDED CORRECTIONS (format_fixes.yml) — expected to differ")
        print("-" * W)
        for e, p, fx in covered:
            print(f"  {p['file']}")
            print(f"      kind   : {fx.get('kind')}")
            print(f"      blob   : {str(fx.get('fixed_blob'))[:12]}")
            print(f"      reason : {str(fx.get('reason'))[:150]}")

    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())

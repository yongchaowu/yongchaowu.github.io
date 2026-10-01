#!/usr/bin/env python3
"""Sync post bodies from the cnblogs export (source of truth) into _posts/.

What this is for
----------------
The repository was imported before the 2026-09-25 upstream proofread pass and
nothing re-synced it: articles showed version facts the upstream had since
corrected. This performs that re-sync. It replaces bodies only -- never front
matter, never filenames, never dates -- so no published URL can move.

Everything that decides "what should this post be" lives in upstream_text.py,
shared with compare_upstream.py. That sharing is not tidiness. The two scripts
each carried their own copy of the rules, and they answered differently: the
report called 90 articles drifted right after a clean sync, because it did not
know about the corrections this repository makes on top of upstream (`%20` link
targets, repaired empty-target links, re-applied format_fixes.yml rules), and
called 68 once those were applied, because it still used strict equality where
the writer used typographic equivalence. A report that overstates outstanding
work by 3.5x is worse than no report, so there is now one definition, and this
file is only the part that reads files and writes them.

Three classes are never touched, because overwriting them would destroy work
rather than sync it:

  * `curated: true` posts -- net-new synthesized guides with no upstream source.
  * the merged llm-probe post -- Blog Garden received that article as two parts
    because of its 200 KB cap, so there is no single file to merge from.
  * the seven export files with no public URL (four private diary entries, a book
    list, a team-building retrospective, a library note). They were never
    published; importing them would publish them.

And from 2026-06 on, nothing is written automatically. Editing happens here and
publishes outward, so the flow reverses -- and reverses *inconsistently*: of the 42
paired posts in that era, 14 are behind upstream, 1 is ahead of it, 2 carry the
proofread mark on both sides. Those are reported for review. Copying upstream
would, in at least one documented case, restore content this site has already
corrected.

Usage
-----
    python3 scripts/sync_upstream.py              # dry run: report, write nothing
    python3 scripts/sync_upstream.py --execute    # write, after reading the dry run
    python3 scripts/sync_upstream.py --only SUBSTRING --verbose
"""
import argparse
import difflib
import importlib.util
import json
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))


def _shared():
    spec = importlib.util.spec_from_file_location(
        "upstream_text", os.path.join(_HERE, "upstream_text.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


T = _shared()


def load_parts(path):
    """Return (whole file, front matter including delimiters, body).

    The no-front-matter case must return the whole file as the body. It is not a
    corner case: 326 of the 337 paired cnblogs exports have no front matter at all
    and start directly with the `# title` line. Returning "" here would make the
    sync overwrite 326 substantive articles with nothing, and the dry run is the
    only reason that was caught rather than written.
    """
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read()
    m = T.FM_RE.match(raw)
    if not m:
        return raw, "", raw
    return raw, m.group(0), raw[m.end():]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true",
                    help="actually write (default is a dry run)")
    ap.add_argument("--only", help="restrict to filenames containing this")
    ap.add_argument("--verbose", action="store_true", help="show block diffs")
    args = ap.parse_args()

    os.chdir(os.path.dirname(_HERE))
    pairing_spec = importlib.util.spec_from_file_location(
        "pair_upstream", os.path.join(_HERE, "pair_upstream.py"))
    pairing = importlib.util.module_from_spec(pairing_spec)
    pairing_spec.loader.exec_module(pairing)

    proc = subprocess.run([sys.executable, "scripts/pair_upstream.py", "--json"],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stdout + proc.stderr)
        print("\nrefusing to sync: the pairing is not fully resolved", file=sys.stderr)
        return 2
    pairs = json.loads(proc.stdout)["pairs"]

    rules = T.load_recorded_fixes()

    def rule_key(name):
        return name if name.startswith("_posts/") else "_posts/" + name

    def rules_for(name):
        key = rule_key(name)
        return {key: rules[key]} if key in rules else {}

    changed = skipped = tier1 = tier2 = 0
    held, ahead, lost_facilities, reinstated, links_fixed = [], [], [], [], []
    written = []

    for pr in pairs:
        post = pr["post"]
        if args.only and args.only not in post:
            continue
        r_raw, r_fm, r_body = load_parts(os.path.join("_posts", post))
        _, _, u_body = load_parts(os.path.join(pairing.EXPORT_DIR, pr["export"]))
        u_body = T.strip_leading_h1(u_body, pr["export_title"])

        # A locally corrected post is never overwritten by upstream content that
        # lacks the correction, so an upstream-absent proofread mark means this
        # repository already said something the source of truth has not.
        if (T.flow_direction(post, r_raw) == "local"
                and not T.bodies_equivalent(u_body, r_body)
                and T.proofread_mark(r_body) and not T.proofread_mark(u_body)):
            ahead.append(post)
            continue

        if u_body == r_body or T.bodies_equivalent(u_body, r_body):
            # Already in sync with upstream -- but the local copy can still be
            # defective in ways the upstream copy shares. An empty-target link
            # renders as a live-looking anchor that goes nowhere, and a recorded
            # fix may have been undone by an edit. Both are repaired here rather
            # than left alone because "no sync was needed": being in sync with the
            # source of truth is not the same as being correct.
            #
            # The recorded-fix half matters more than it looks. cnblogs still holds
            # `http://meldmerge.org/images/`, so reverting this file makes the two
            # sides identical again -- and a naive "no diff, skip" would then leave
            # three screenshots as active mixed content indefinitely.
            fixed, n = T.repair_broken_links(r_body)
            fixed, n2 = T.encode_link_target_whitespace(fixed)
            fixed, n3 = T.apply_recorded_fixes(fixed, rules, rule_key(post))
            if n + n2 + n3:
                if n + n2:
                    links_fixed.append((post, n + n2))
                if n3:
                    reinstated.append(post)
                written.append((post, r_fm + fixed, r_body, fixed))
                changed += 1
                tier1 += 1
            else:
                skipped += 1
            continue

        if T.flow_direction(post, r_raw) == "local":
            held.append(post)
            continue

        if len(u_body.strip()) < 5 < len(r_body.strip()):
            # Refuse rather than infer: an empty upstream body for a substantive
            # post is a defect upstream, and guessing would delete the article.
            lost_facilities.append((post, f"upstream empty ({len(u_body)} chars)"))
            continue

        want, notes = T.expected_body(u_body, r_body, rules_for(post), post)
        if notes.get("lost"):
            lost_facilities.append((post, notes["lost"]))

        if want == r_body or T.bodies_equivalent(want, r_body):
            skipped += 1
            continue

        if any(notes.get(k) for k in ("links_missing", "raw_missing")) or \
                notes.get("raw_no_longer_needed"):
            links_fixed.append((post, len(notes.get("raw_no_longer_needed", []))))
        if any(n in u_body for n in rules.get(rule_key(post), ("", []))[1]):
            _, was_reapplied = T.apply_recorded_fixes(u_body, rules_for(post), post)
            if was_reapplied:
                pass          # upstream still holds the defect; nothing to re-apply
        tier1 += (notes["tier"] == 1)
        tier2 += (notes["tier"] == 2)
        changed += 1
        written.append((post, r_fm + want, r_body, want))
        if args.verbose:
            for line in list(difflib.unified_diff(
                    r_body.split("\n"), want.split("\n"),
                    fromfile="repo/" + post,
                    tofile="upstream/" + pr["export"], lineterm="", n=1))[:60]:
                print(line)

    W = 64
    print("=" * W)
    print("Upstream -> repository body sync" +
          ("" if args.execute else "  [DRY RUN]"))
    print("=" * W)
    print(f"  paired articles            {len(pairs)}")
    print(f"  body already current       {skipped}")
    print(f"  WOULD change               {changed}")
    print(f"    tier 1 (no Liquid)       {tier1}")
    print(f"    tier 2 (Liquid, masked)  {tier2}")
    print()
    print(f"  held back for review       {len(held) + len(ahead)}"
          f"   (flow direction is not forward)")
    print(f"    already ahead of upstream {len(ahead)}")
    print(f"    direction mixed          {len(held)}")
    for post in ahead:
        print(f"      AHEAD {post[:58]}")
    for post in held:
        print(f"      MIXED {post[:58]}")
    if links_fixed:
        print(f"\n  repaired text defects      "
              f"{sum(n for _, n in links_fixed)} in {len(links_fixed)} posts")
        for post, n in links_fixed:
            print(f"       {post[:62]}  ({n})")
    if reinstated:
        print(f"  re-applied recorded corrections  {len(reinstated)}")
        for post in reinstated:
            print(f"       {post[:62]}")
    if lost_facilities:
        print(f"\n  !! refused / lost facilities: {len(lost_facilities)}")
        for post, why in lost_facilities:
            print(f"       {post[:58]}  {why}")
        print("     These need a human: a `raw` wrapper or `post_url` link sits in")
        print("     prose the upstream rewrote, so it cannot be re-anchored safely.")
    else:
        print("\n  Jekyll-side facility blocks (<!--more-->, {% raw %}, "
              "{% post_url %}) all survive.")

    if args.execute:
        for post, new_raw, _, _ in written:
            path = os.path.join("_posts", post)
            # Preserve whether the original ended with a newline. A cnblogs export
            # strips the final newline on 196 of 346 files and 183 posts here
            # inherited that; appending one is a spurious 1-byte diff that
            # verify-post-history.rb would reject.
            ends_nl = open(path, "rb").read().endswith(b"\n")
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(new_raw if ends_nl else new_raw.rstrip("\n"))
        print(f"\n  wrote {len(written)} files")
    else:
        print(f"\n  nothing written. Re-run with --execute to apply.")
    return 1 if lost_facilities else 0


if __name__ == "__main__":
    sys.exit(main())

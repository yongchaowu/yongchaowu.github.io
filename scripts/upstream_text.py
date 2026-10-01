#!/usr/bin/env python3
"""Shared text handling for comparing and syncing against the cnblogs export.

Both scripts/compare_upstream.py (report) and scripts/sync_upstream.py (write)
have to agree on two questions:

  1. what transformations the importer performed on purpose, and
  2. what this repository corrects on top of upstream.

They used to answer (2) differently, which made the report lie. After a sync the
report still counted 90 articles as "differ in substance", while only 25 were
actually awaiting review -- the other 65 differed solely by corrections this
repository makes deliberately (`%20` in a link target, an empty-target link
turned into an autolink, a recorded fix from format_fixes.yml re-applied). A
number that overstates the outstanding work by 3.5x is worse than no number, so the
logic lives here once and both callers import it.

The corrections themselves, and why each exists:

`repair_broken_links`
    Upstream carries `[text]()`, which kramdown renders as `<a href="">text</a>`
    -- a live-looking anchor that goes nowhere. Two shapes, two repairs: when the
    URL is present in the text (`[https://h/p]()`) it becomes an autolink, and
    when it is absent (`[FileZilla Server]()`) the text is kept unlinked, since
    cnblogs dropped the target and inventing one would be worse. It must skip
    fenced code: six of the eleven apparent hits on a whole-file regex were C++
    lambdas, `[this](){}`.

`encode_link_target_whitespace`
    A literal space is not legal in a link target. Encoding it makes the href
    valid and keeps the author's target. Note what this does not do: it does not
    make the link resolve. `http://down.52pojie.cn/Tools/PEtools/PEiD 0.95.rar`
    answers 404 with or without the encoding, because the file is gone from the
    server. A dead external link from 2019 is the archive's business.

`apply_recorded_fixes`
    Re-applies the `rewrite` rules in _data/format_fixes.yml. cnblogs still
    carries `http://meldmerge.org/images/`, so an upstream copy reinstates active
    mixed content on three screenshots and smoke-test.rb fails again. A recorded
    correction is only real if it stays applied.
"""
import os
import re
import unicodedata
from collections import Counter

FORMAT_FIXES = os.path.join("_data", "format_fixes.yml")

FM_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.S)
H1_RE = re.compile(r"^\s{0,3}#(?!#)\s*(.+?)\s*$", re.M)
BLOCK_SPLIT_RE = re.compile(r"\n\s*\n")
FENCE_SPLIT_RE = re.compile(
    r"(^[ \t]*`{3,}[^\n]*$.*?^[ \t]*`{3,}[^\n]*$)", re.S | re.M)
RAW_BLOCK_RE = re.compile(r"{%-?\s*raw\s*-?%}.*?{%-?\s*endraw\s*-?%}", re.S)
RAW_PAIR_RE = re.compile(
    r"\A{%-?\s*raw\s*-?%}(?P<payload>.*?){%-?\s*endraw\s*-?%}\Z", re.S)
# `{% post_url X %}` appears in two shapes and both occur here:
#
#   [visible text]({% post_url 2026-06-12-...-Ray(Docker) %})   <- the link text
#                                                                is OUTSIDE the tag
#   {% post_url ... %}visible text)                             <- emitted inline
#
# The first is the more common one here, and it is the one a pattern expecting
# text after the tag misses. Consequence, measured: re-applying internal links
# dropped both cross-references in
# 2026-06-12-Python-Ray-Offline-Installation-Guide.md while reporting no loss.
# Shape one is matched whole, so the inline alternative cannot match inside one.
POST_URL_RE = re.compile(
    r"(?:\[[^\]\n]{1,120}\]\({%-?\s*post_url\s+[^%\n]*?-?%}\)"
    r"|{%-?\s*post_url\s+(?P<slug>[^%\n]*?)\s*-?%}(?P<text>[^()\n]{1,80}?\)))")
BROKEN_LINK_WITH_URL_RE = re.compile(r"\[(https?://[^\]\n]{4,200}?)\]\(\s*\)")
BROKEN_LINK_TEXT_RE = re.compile(r"\[([^\]\n]{1,120}?)\]\(\s*\)")
LINK_TARGET_RE = re.compile(r"\]\(((?:https?|ftp)://[^)\n]*)\)")
LIQUID_HAZARD_RE = re.compile(r"\{\{|\{%|\{#")

DATE_RE = re.compile(r"^(\d{4})-(\d{2})")

# The direction of the content flow is not uniform across the archive.
#
# Before 2026-06 every article was imported from cnblogs, so cnblogs is the source
# of truth and syncing upstream is unambiguously forward. Measured 2026-10-01 over
# the 295 paired posts in this era: 42 already identical, 174 carry the upstream
# 2026-09-25 proofread mark and this repository does not, 79 differ some other
# way, and **none** is ahead of upstream.
#
# From 2026-06 on, editing happens here and publishes outward, so the direction
# reverses -- and it reverses *inconsistently*. Over the 42 paired posts in this
# era: 17 identical, 14 behind upstream, 1 ahead of it (2026-09-05
# New-API-Multi-Process-Docker carries an upstream-absent `> 重要勘误（2026-09-25）`
# saying the old built-in-worker design is withdrawn), 2 marked on both sides, 8
# differing another way. That era is reported for review, never written
# automatically: copying upstream would, in at least one documented case, restore
# content this site has already corrected.
FLOW_REVERSES = ("2026", "06")


def front_matter_field(body_or_text, name):
    """Read one front-matter field without a YAML dependency at call time."""
    fm, _ = split_front_matter(body_or_text)
    m = re.search(r"^%s:\s*(.*?)\s*$" % re.escape(name), fm, re.M)
    return m.group(1).strip().strip("\"'") if m else None


def flow_direction(post_name, repo_body=None):
    """'imported' = cnblogs is the source and syncing is forward.
    'local'    = this repository is the source; direction is mixed, review it.

    `upstream_sync: off` in a post's front matter overrides the date rule and
    wins outright. The date threshold is a fallback, not a decision: it happened
    to place every post with a local correction after 2026-06, but nothing about
    a post's content depends on when it was written, and one date edit away from
    a silently reverted fix. The override carries its reason in
    `upstream_sync_reason`, so the next reader sees the evidence rather than a
    date they would have to reconstruct.
    """
    if repo_body is not None:
        flag = front_matter_field(repo_body, "upstream_sync")
        if flag and flag.lower() in ("off", "false", "no"):
            return "local"
    m = DATE_RE.match(post_name)
    if not m:
        return "unknown"
    return "local" if (m.group(1), m.group(2)) >= FLOW_REVERSES else "imported"


MORE_RE = re.compile(r"<!--\s*more\s*-->")

CODE_FENCE_RE = re.compile(r"```.*?```", re.S)

INLINE_CODE_RE = re.compile(r"`[^`\n]*`")

HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)

LIQUID_RAW_RE = re.compile(r"\{%-?\s*(raw|endraw)\s*-?%\}")

MD_LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")

CJK = r"\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\u3040-\u30ff"
HEADING_SPACE_RE = re.compile(r"^(#{1,6})\s*(?=\S)", re.M)
CJK_LATIN_SPACE_RE = re.compile(
    rf"(?<=[{CJK}])\s+(?=[A-Za-z0-9])"      # CJK then Latin
    rf"|(?<=[A-Za-z0-9])\s+(?=[{CJK}])"      # Latin then CJK
    rf"|(?<=[{CJK}])\s+(?=[，。；：、）】」』])|(?<=[（【「『])\s+(?=[{CJK}])")

VERSION_RE = re.compile(r"\b(\d+\.\d+(?:\.\d+)?)\b")

DECL_MARKERS = ("AI 修改声明", "AI修订声明", "修改声明", "本文由 LLM",
                "LLM 协助", "本文修订依据")


def normalize_body(body, title=""):
    """Reduce a post body to comparable prose.

    Removes the transformations the importer performs on purpose, so that what
    remains is genuine content drift.
    """
    b = body
    b = LIQUID_RAW_RE.sub("", b)              # raw wrappers added/removed
    b = MORE_RE.sub("", b)                    # excerpt marker placement
    b = HTML_COMMENT_RE.sub("", b)            # any other comment
    # Fence info strings are formatting; the fence body is content. Keep the
    # body, drop the language tag: the importer repairs malformed tags and that
    # must not be reported as drift.
    b = re.sub(r"^(\s*)(`{3,})[^\n`]*$", r"\1\2", b, flags=re.M)
    b = MD_LINK_RE.sub(r"\1\2", b)            # link text only, drop the target
    b = re.sub(r"\r\n", "\n", b)
    # Drop a leading H1 that merely restates the title: the layout renders it.
    lines = b.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines:
        m = H1_RE.match(lines[0])
        if m and (not title or loose_key(m.group(1)) == loose_key(title)):
            lines.pop(0)
    b = "\n".join(lines)
    # A line holding only spaces has to become a genuinely empty line before the
    # blank-line collapse below. Without this, `[ \t]+ -> " "` leaves those lines
    # as " ", the `\n{2,}` pattern no longer matches them, and two bodies that
    # differ only in trailing whitespace compare as different -- which is how
    # 2024-04-23-Tool-Gitlab-重置root账户密码 showed up as "not yet synced"
    # long after it had been.
    b = re.sub(r"^[ \t]+$", "", b, flags=re.M)
    b = re.sub(r"[ \t]+", " ", b)
    b = re.sub(r"\n{2,}", "\n", b)           # blank lines are formatting too
    return b.strip()


def word_set(text):
    return set(re.findall(r"[0-9a-zA-Z一-鿿]+", text.lower()))


def typographic_normalize(text):
    """Undo the proofread pass's spacing normalisation."""
    t = HEADING_SPACE_RE.sub(r"\1 ", text)
    prev = None
    while prev != t:                          # spacing edits can cascade
        prev = t
        t = CJK_LATIN_SPACE_RE.sub("", t)
    return t


def is_declaration_only(upstream, repo):
    """True when the sole difference is an upstream AI/revision declaration."""
    def strip(s):
        return "\n".join(ln for ln in s.split("\n")
                          if not any(mk in ln for mk in DECL_MARKERS))
    return strip(upstream) == strip(repo)


def version_delta(upstream, repo):
    """Return version-like tokens present on one side only."""
    uv = Counter(VERSION_RE.findall(upstream))
    rv = Counter(VERSION_RE.findall(repo))
    return sorted((uv - rv).elements()), sorted((rv - uv).elements())


def norm_key(text):
    return re.sub(r"[^0-9a-z一-鿿]+", "", text.lower())


def split_front_matter(text):
    m = FM_RE.match(text)
    if not m:
        return "", text
    return m.group(1), text[m.end():]


def proofread_mark(body):
    """Whether this body carries the 2026-09-25 proofread/errata notice."""
    return ("修改声明" in body or "本文修订依据" in body or "勘误" in body)


def loose_key(text):
    """Loose identifier: NFKC, entities decoded, only letters/digits/CJK.

    Stronger than `norm_key` on purpose. It has to undo the systematic rewrites
    between the two sides, or articles pair by nothing at all: cnblogs export
    filenames use HTML entities and spaces (`Code-C++-CTime&amp;ColeDateTime`,
    `Libevent-windows 编译&引用`) while the posts spell those out
    (`...CTimeandColeDateTime`, `...编译and引用`).
    """
    text = unicodedata.normalize("NFKC", text)
    text = (text.replace("&amp;", "&").replace("&#183;", "·")
                .replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"'))
    # `&` becomes the word "and" in Jekyll filenames. Without this,
    # Code-C++-CTime&amp;ColeDateTime pairs with nothing at all.
    text = text.replace("&", " and ")
    return re.sub(r"[^0-9a-z一-鿿]+", "", text.lower())


def bodies_equivalent(upstream, repo):
    """True when the two bodies say the same thing.

    The AI/revision declaration is deliberately *not* absorbed: it is visible text
    on one domain and absent on the other, which is a divergence to resolve, not
    formatting to forgive.
    """
    a = normalize_body(upstream, "")
    b = normalize_body(repo, "")
    if a == b:
        return True
    return typographic_normalize(a) == typographic_normalize(b)


def strip_leading_h1(body, title):
    """Drop a body H1 only when it restates the title; the layout renders that."""
    lines = body.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines:
        m = H1_RE.match(lines[0])
        if m and (not title or norm_key(m.group(1)) == norm_key(title)):
            return "\n".join(lines[1:]).lstrip("\n")
    return body


def expected_body(upstream_body, repo_body, rules=None, post_path=None):
    """What this repository's copy of `upstream_body` should be.

    The single definition of "synced". Both callers need this exact question
    answered -- the report to classify a post, the writer to decide whether to
    write it -- and while each carried its own version they answered differently:
    after a clean sync the report still called 90 articles drifted because it did
    not know about `%20`, repaired empty-target links, or re-applied fixes. Then
    it called 68 once the corrections were applied, because it still used strict
    equality where the writer used typographic equivalence. One function removes
    the possibility.

    Returns (body, notes) where notes describes the facilities that were carried
    over, for reporting.
    """
    notes = {"tier": 1, "raw_blocks": 0, "links": "0/0", "more": 0}
    mi = more_index(repo_body)
    if LIQUID_HAZARD_RE.search(repo_body) or POST_URL_RE.search(repo_body) \
            or RAW_BLOCK_RE.search(repo_body):
        # A protected region is present, so prose is replaced wholesale and the
        # wrappers are re-anchored by content signature and fence boundaries.
        # Block alignment is not usable: on 2020-07-11-Code-OPC-DA, masking the
        # facilities into atoms still lost both of them, because the article was
        # rewritten wholesale and SequenceMatcher matched nothing to anchor on.
        notes["tier"] = 2
        body, notes2 = _merge_protected(repo_body, upstream_body)
        notes.update(notes2)
    else:
        body = (ensure_more_outside_raw(insert_more(upstream_body, mi))
                if mi is not None else upstream_body)
    body, _ = repair_broken_links(body)
    body, _ = encode_link_target_whitespace(body)
    # `post_path` is required for the recorded fixes to apply. It was previously
    # passed as the literal "_posts/x", so the lookup never matched and the
    # meldmerge https rewrite was silently dropped from every rebuild -- the file
    # stayed correct only because an older version of the writer had already fixed
    # it. A correction that quietly stops being re-applied is the failure mode
    # format_fixes.yml exists to prevent, so the argument is explicit.
    if rules and post_path:
        body, _ = apply_recorded_fixes(body, rules, post_path)
    return body, notes


def _merge_protected(repo_body, upstream_body):
    """Take upstream wholesale, re-attaching raw wrappers, links and more."""
    raw_blocks = [m.group(0) for m in RAW_BLOCK_RE.finditer(repo_body)]
    links_before = len(POST_URL_RE.findall(repo_body))

    body = upstream_body
    restored = 0
    absent = []
    for m in POST_URL_RE.finditer(repo_body):
        # Shape one keeps its visible text outside the tag, so `text` is None and
        # there is nothing inside the match to search for. Anchor on the text the
        # reader sees instead.
        text = (m.group("text") or "").strip()
        if not text:
            vis = re.match(r"\[([^\]\n]{1,120})\]", m.group(0))
            text = vis.group(1) if vis else ""
        if text and text in body:
            body = body.replace(text, m.group(0), 1)
            restored += 1
        else:
            # Two different situations, and conflating them sends the reader to
            # the wrong conclusion. Either upstream still has this text and the
            # anchor failed -- a bug here -- or upstream no longer contains it at
            # all, in which case the anchor had nothing to match and the link
            # simply has no host. 2026-06-12-Python-Ray-Offline is the second:
            # upstream dropped the whole "Next Steps" section, so both
            # cross-references vanished with it.
            absent.append(text[:60])

    body, raws_done, dropped, missing = _reapply_raw(body, raw_blocks)

    mi = more_index(repo_body)
    more_done = 0
    if mi is not None and "<!--more-->" not in body:
        body = insert_more(body, mi)
        more_done = 1
    body = ensure_more_outside_raw(body)

    # `lost` counts only what should have been recoverable and was not. A link
    # whose target text upstream no longer has is not a loss -- it is content the
    # upstream rewrite removed, and it belongs in `upstream_dropped` so a reader of
    # the report can tell "the tool broke" from "the source no longer has it".
    lost = len(missing) + (1 if mi is not None and more_done == 0 else 0)
    return body, {"raw_blocks": len(raw_blocks), "links": f"{restored}/{links_before}",
                  "more": more_done, "lost": lost,
                  "upstream_dropped": absent,
                  "raw_no_longer_needed": dropped, "raw_missing": missing,
                  "kept": restored + raws_done + more_done}


def _reapply_raw(upstream_body, raw_blocks):
    """Re-wrap protected content, but only where protection is still needed.

    A `{% raw %}` block exists to stop Liquid from interpreting braces in a JSON or
    C snippet. If the upstream rewrite removed every such brace the wrapper adds
    nothing, and forcing it back is guesswork: on 2020-07-11-Code-OPC-DA the
    upstream text became a citation link, so the original payload is not present
    and no signature can find it. Where protection *is* still needed and the text
    signature is gone, the fenced code block is used as the boundary, because
    fences survive any amount of prose rewriting. That case decides whether the
    build survives: an unwrapped `{{&IID_OPCServer,` is read as a Liquid output
    tag and the article renders with a hole in it.
    """
    body, restored, dropped, missing = upstream_body, 0, [], []
    for block in raw_blocks:
        inner = RAW_PAIR_RE.match(block)
        payload = inner.group("payload") if inner else block
        if not LIQUID_HAZARD_RE.search(payload):
            dropped.append(payload.strip()[:60])
            continue
        head = payload.strip()[:120]
        idx = body.find(head)
        if idx >= 0:
            body = body[:idx] + block + body[idx + len(head):]
            restored += 1
            continue
        hazard = LIQUID_HAZARD_RE.search(payload)
        anchor = payload[hazard.start():hazard.start() + 60].strip().split("\n")[0]
        pos = body.find(anchor)
        span = fenced_span_around(body, pos) if pos >= 0 else None
        if span is None:
            missing.append(anchor[:60])
            continue
        open_at, close_at = span
        if body[max(open_at - 9, 0):open_at] == "{% raw %}":
            restored += 1
            continue
        body = (body[:open_at] + "{% raw %}\n" + body[open_at:close_at]
                + "{% endraw %}\n" + body[close_at:])
        restored += 1
    return body, restored, dropped, missing


def fenced_span_around(body, pos):
    """Return (start, end) of the fenced code block containing `pos`.

    Falls back to a paragraph span so a bare inline brace is still protected.
    """
    open_re = re.compile(r"^[ \t]*(`{3,}|~{3,})", re.M)
    best = None
    for m in open_re.finditer(body):
        if m.start() > pos:
            break
        best = m
    if best is not None:
        marker = best.group(1)
        close_re = re.compile(r"^[ \t]*" + re.escape(marker[0]) +
                              "{" + str(len(marker)) + ",}[ \t]*$", re.M)
        cm = close_re.search(body, best.end())
        if cm and cm.start() > pos:
            return best.start(), cm.end()
    start = body.rfind("\n\n", 0, pos)
    start = 0 if start < 0 else start + 2
    end = body.find("\n\n", pos)
    end = len(body) if end < 0 else end
    return start, end


def repair_broken_links(body):
    """`text[url]()` -> `text <url>`; `[text]()` -> `text`. See module docstring."""
    parts = FENCE_SPLIT_RE.split(body)
    repaired = 0
    for i, part in enumerate(parts):
        if i % 2 == 1:            # inside a fence: leave C++ alone
            continue
        part, n1 = BROKEN_LINK_WITH_URL_RE.subn(r"<\1>", part)
        part, n2 = BROKEN_LINK_TEXT_RE.subn(r"\1", part)
        parts[i] = part
        repaired += n1 + n2
    return "".join(parts), repaired


def encode_link_target_whitespace(body):
    parts = FENCE_SPLIT_RE.split(body)
    count = 0
    for i, part in enumerate(parts):
        if i % 2 == 1:
            continue

        def repl(m):
            nonlocal count
            target = m.group(1)
            if " " not in target:
                return m.group(0)
            # `[t](url "title")` also contains a space; encoding it breaks the link.
            if '"' in target or "'" in target:
                return m.group(0)
            count += 1
            return "](" + target.replace(" ", "%20") + ")"

        parts[i] = LINK_TARGET_RE.sub(repl, part)
    return "".join(parts), count


def load_recorded_fixes(path=FORMAT_FIXES):
    """Load `rewrite` rules from _data/format_fixes.yml, keyed by post path."""
    rules = {}
    if not os.path.isfile(path):
        return rules
    try:
        import yaml
    except ModuleNotFoundError:
        return rules
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    for entry in data.get("fixes") or []:
        if isinstance(entry, dict) and entry.get("post") and entry.get("rewrite"):
            rules[entry["post"]] = (entry["rewrite"], entry.get("reapply") or [])
    return rules


def apply_recorded_fixes(body, rules, post_path):
    """Apply this post's recorded rewrite. Returns (body, was_reinstated)."""
    key = post_path if post_path.startswith("_posts/") else "_posts/" + post_path
    if key not in rules:
        return body, False
    rewrite, needles = rules[key]
    if not any(n in body for n in needles):
        return body, False
    old, _, new = rewrite.partition(" -> ")
    if not new:
        return body, False
    return body.replace(old, new), True


def more_index(body):
    """Block index at which `<!--more-->` sits, or None if absent."""
    if "<!--more-->" not in body:
        return None
    head = body.split("<!--more-->", 1)[0]
    return len([b for b in BLOCK_SPLIT_RE.split(head) if b.strip()])


def insert_more(body, index):
    """Re-insert `<!--more-->` at the same block index it occupied before."""
    if index is None:
        return body
    blocks = BLOCK_SPLIT_RE.split(body)
    idx = min(index, max(len(blocks) - 1, 1))
    return "\n\n".join(blocks[:idx + 1]) + "\n\n<!--more-->\n\n" + \
        "\n\n".join(blocks[idx + 1:])


def ensure_more_outside_raw(body):
    """Hoist `<!--more-->` out of any {% raw %} block it landed inside.

    Jekyll warns and rewrites the excerpt when the separator sits in a Liquid
    block, and names the file: it appeared on
    2020-07-11-Code-OPC-DA-OPC-Client-Code-Demo, where the marker landed between
    the opening fence and the body of a code sample. The marker means "the excerpt
    ends here", so hoisting it above the protected block is the only reading that
    keeps the excerpt prose.
    """
    for _ in range(8):                     # raw blocks may nest after re-wrapping
        pos = body.find("<!--more-->")
        if pos < 0:
            return body
        raw_open = body.rfind("{% raw %}")
        if raw_open < 0 or pos < raw_open:
            break
        raw_close = body.find("{% endraw %}", raw_open)
        if raw_close < 0 or pos > raw_close:
            break
        body = body[:pos] + body[pos + len("<!--more-->"):]
        raw_open = body.rfind("{% raw %}")
        body = body[:raw_open] + "<!--more-->\n\n" + body[raw_open:]
    return body

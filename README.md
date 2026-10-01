# yongchaowu.github.io

Personal engineering notebook of **Yc.W (@yongchao)** — <https://blog.wyclswq.top>

Tech notes on C++, OS, developer tooling, and AI/LLM infrastructure. The articles were
first published on cnblogs — <https://www.cnblogs.com/yongchao> — and are then corrected,
refined, organized and synthesized here. See [`AGENTS.md`](AGENTS.md) for the content
supply chain and [`docs/review-2026-10-01.md`](docs/review-2026-10-01.md) for the latest
engineering review.

- Jekyll 4 on GitHub Pages, theme based on [HyG's](https://github.com/Gaohaoyang/gaohaoyang.github.io)
- 357 posts, 19 curated guides, 11 topics, 277 tags, plus a reading-path layer at
  <https://blog.wyclswq.top/start-here/>
- RSS at <https://blog.wyclswq.top/feed.xml>

## Build

```bash
bundle exec jekyll clean
TZ=UTC bundle exec jekyll build        # ~40s
```

## Validation

Everything below must pass before proposing a commit. CI runs all of it
(`.github/workflows/pages.yml`).

```bash
# Generated data. Both are committed, so both have a --check mode that CI runs
# to catch a stale file. Re-run the generators after adding, editing or removing
# any post, or after changing tag/slug data.
uv run --with-requirements scripts/requirements.txt scripts/generate_post_meta.py
uv run --with-requirements scripts/requirements.txt scripts/generate_post_meta.py --check
uv run --with-requirements scripts/requirements.txt scripts/generate_tag_pages.py
uv run --with-requirements scripts/requirements.txt scripts/generate_tag_pages.py --check

# Content and structure
ruby scripts/audit-content.rb          # taxonomy; advisory, reports but does not fail
ruby scripts/validate-curation.rb      # front matter, curated sources, reading paths, sidecars
ruby scripts/validate-tags.rb          # every active tag has a route; no slug collisions

# Generated site
ruby scripts/smoke-test.rb             # routes, JSON indexes, links, plus content/metadata claims
python3 scripts/site-review.py         # landmarks, headings, controls, current state
node scripts/search-interaction-test.js

# Preserved history
ruby scripts/verify-post-history.rb    # 331 baseline blobs + explicit format_fixes.yml exceptions

# JavaScript syntax
for f in js/*.js; do node --check "$f"; done
```

Two traps worth knowing:

- `site-review.py` prints only the first 20 warnings, so per-post counts have to be
  checked by hand.
- kramdown auto-ids do not match GitHub slugs, so in-page TOC anchors are not covered by
  `smoke-test.rb` and have to be verified manually.

## Content policy

- Historical post bodies, dates and generated URLs are preserved. A deliberate correction
  to a preserved post is recorded in [`_data/format_fixes.yml`](_data/format_fixes.yml)
  against an exact resulting blob, with a stated reason — never applied silently.
- Editorial metadata (`_data/post_editorial.yml`) is descriptive, not evidence. Nothing is
  called verified or current unless a source in the repository or an attached reference
  supports it. Version-sensitive, AI-assisted, imported and unverified states stay visible.
- `_drafts/` is not tracked. Jekyll never builds it, but git has no notion of "private" —
  anything committed there is in every clone and archivable by third parties. Unpublished
  work lives in `~/Workspace/Blog/ref/`.
- `vendor/` and `.bundle/` are not tracked. `.bundle/config` pins `BUNDLE_PATH` to
  `vendor/bundle`, so without the ignore rules a local `bundle install` plus `git add -A`
  puts ~3,200 files and 56 MB of native binaries into history.

## Related documents

| | |
|---|---|
| [`AGENTS.md`](AGENTS.md) | operational rules, content supply chain, validation contract |
| [`docs/review-2026-10-01.md`](docs/review-2026-10-01.md) | full engineering review, findings, corrections, remediation record |
| [`docs/technical-review-2026-09-25.md`](docs/technical-review-2026-09-25.md) | external factual cross-checks of article claims |
| [`docs/content-optimization.md`](docs/content-optimization.md) | content baseline |

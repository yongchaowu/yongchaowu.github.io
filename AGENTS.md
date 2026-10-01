# Agent notes

## Content supply chain — read this first

This repository is **not the source of truth for the articles**. It is the derived
publication target. The chain is:

```
cnblogs (source of truth)  ->  ~/Workspace/Blog/  ->  this repo  ->  https://blog.wyclswq.top
```

- **Upstream blog (母本 / source of truth):** <https://www.cnblogs.com/yongchao>.
  Articles were published there first. Public article URLs are
  `https://www.cnblogs.com/yongchao/p/<postId>.html`.
- **Upstream workspace:** `~/Workspace/Blog/`. Read `~/Workspace/Blog/AGENTS.md` before
  touching anything upstream — it is the authoritative document for the cnblogs side
  (evidence standard, 200 KB per-post cap, publish/verify loop, credential handling).
- **Latest backup of the current blog:** `~/Workspace/Blog/backup/`
  (`cnblogs_blog_yongchao.<timestamp>.zip`, 1.2 MB, latest
  `cnblogs_blog_yongchao.20261001000949.zip`). The extracted mirror beside it,
  `~/Workspace/Blog/cnblogs_blog_yongchao.<timestamp>/yongchao/`, held **346 articles** at
  the 2026-10-01 export. That zip is the rollback mechanism for a published article, not git.
- **This repository's job** is the second half of the stated project: after cnblogs
  publication, *correct, refine, organize and synthesize* the material into a
  self-owned blog. That is what `_data/post_editorial.yml`, the curated layer, reading
  paths, and the topics taxonomy are for.
- **Consequence for every rule below:** an article's body here may legitimately differ
  from the cnblogs original, because the import deliberately adapts front matter
  (`description` -> `summary`, add `layout`/`display_title`/`lang`/`categories`, drop the
  body H1 because the layout renders the title) and because the curation pass corrects
  facts. The blob baseline and `format_fixes.yml` exist to keep that divergence
  auditable, not to forbid it. Corrections land here first; whether they are pushed back
  upstream is a separate, explicit decision made in `~/Workspace/Blog/`, not a side effect
  of committing here.
- **Do not treat "it matches cnblogs" as a defect, and do not treat "it differs from
  cnblogs" as an error.** Both states are expected. What is a defect is an *unrecorded*
  divergence — which is what `format_fixes.yml` exists to prevent.

### Known, intentional cross-boundary differences — do not "fix" these

- **llm-probe split.** `~/Workspace/Blog/ref/llm-probe-openai-endpoint-connectivity.md`
  (284,403 B) exceeds Blog Garden's 200 KB per-post cap, so cnblogs received it as
  `llm-probe-1-four-layer-diagnosis` + `llm-probe-2-curl-port-and-key-vault`. This site
  carries the complete single version at
  `_posts/2026-09-30-llm-probe-openai-endpoint-connectivity.md`. Two posts upstream, one
  here, by design.
- **Curated guides are net-new.** 19 posts carry `curated: true` and have no cnblogs
  counterpart; they are synthesized from `source_posts` that do. Note that three of the 19
  are not `curated-*`-prefixed (`2026-09-24-linux-elf-linking-deployment.md`,
  `2026-09-24-modern-cmake-targets-packaging.md`,
  `2026-09-24-modern-cpp-concurrency-lifecycle.md`), so a name-prefix check undercounts them.
- **Trailing newlines are missing on purpose.** A cnblogs export strips the final
  newline: 196 of the 346 exported files end without `\n`, and **183 of the 357 files in
  `_posts/` inherited that**. An editor that appends one produces a 1-byte diff that
  `verify-post-history.rb` will reject. Do not "fix" the newline, and do not spend a
  `format_fixes.yml` exception on it.
- **Filenames are not stable identifiers across the boundary.** Jekyll filenames are
  `YYYY-MM-DD-slug.md`; export filenames have no date prefix. cnblogs also appends an
  unstable `.<postId>` suffix that appears in some snapshots and not others. Match
  articles by normalized name, then title, then content — never by filename alone.
- **A content-hash diff against the export does not work.** Because the import is
  deliberately lossy (front-matter adaptation, H1 removal, excerpt-separator relocation,
  fence repairs), byte or normalized-body comparison reports ~356 of 357 files as
  changed. Upstream drift must be reviewed semantically, per article.

## Repository shape

- This is a Jekyll 4 site deployed to GitHub Pages; there is no Node/package-manager test suite.
- `_posts/` contains the published Markdown articles. `permalink: /:year/:month/:day/:title/` is part of the public URL contract.
- `page/` contains utility pages; `topics/` contains thin topic pages; `_layouts/`, `_includes/`, and `_sass/` implement the site shell and presentation.
- `_data/` is the editorial source of truth: `navigation.yml`, `reading_paths.yml`, `topics.yml`, `post_editorial.yml`, `topic_relations.yml`, `tag_aliases.yml`, `featured_tags.yml`, and the explicit `format_fixes.yml` exception list.
- `post_editorial.yml` stores `posts` as a **mapping keyed by repository-relative post path**, so Liquid reads it with `site.data.post_editorial.posts[path]` (one hash hit) rather than scanning a list. It used to be a list of `{post: ...}` records, which forced a 53-record linear scan into nine templates and twice more per candidate post inside `related-posts.html`. Do not convert it back to a list.
- `post_meta.yml` is **generated**; edit `_posts/` and re-run the generator, never the file. It holds each post's resolved language (`lang`, `lang_source`, `lang_confidence`), its reading statistics, a `reviewed` date where one is traceable, and a `card_summary` used as the last-resort description text by the feed, the search index and the card templates. The 12 posts that are nothing but a code block have no `card_summary`, which is correct — do not invent one for them. The file exists because GitHub Pages runs Jekyll in safe mode, so custom Liquid filters and hooks cannot compute these values at render time. See `scripts/generate_post_meta.py`.
- `search.json` and `posts-meta.json` are Liquid source templates, not hand-maintained generated data. `_site/` is ignored build output; never edit it.
- `scripts/` is repository tooling and is intentionally excluded from the public Pages artifact.

## Content and URL rules

- Preserve historical source files, dates, bodies, and generated post URLs unless the user explicitly asks for a destructive migration. If a historical file needs an intentional formatting or evidence-backed safety correction, record its approved resulting blob and reason in `_data/format_fixes.yml` and update URL/reference audits in the same change.
- The curated layer is additive: curated posts use `curated: true`, `content_origin: curated`, `summary`, `lang`, and repository-relative `source_posts`; validate every source path.
- Editorial metadata is descriptive, not evidence. Do not call a note independently verified/current/authoritative unless the repository or an attached source supports that claim; keep version-sensitive, AI-assisted, imported, historical, and unverified states visible.
- Use `relative_url` for internal links. Keep the canonical routes `/`, `/pageN/`, `/curated/`, `/category/`, `/archive/`, `/tag/`, `/tag/<slug>/`, `/search/`, and `/about/` compatible.
- Do not create `tag/index.md`: `page/2tags.html` is the intentional canonical `/tag/` page and duplicate permalinks break Jekyll.

## Build and verification

Run from the repository root. The local Bundler is vendored; use `bundle exec`.

```bash
# Needed after adding, editing or removing any post, or changing tag/slug data.
# post_meta.yml carries per-post language and reading stats; tag pages carry the
# thin-tag noindex policy. Both are committed generated data, so both have a
# --check mode that CI runs to catch a stale file.
uv run --with-requirements scripts/requirements.txt scripts/generate_post_meta.py
uv run --with-requirements scripts/requirements.txt scripts/generate_post_meta.py --check
uv run --with-requirements scripts/requirements.txt scripts/generate_tag_pages.py
uv run --with-requirements scripts/requirements.txt scripts/generate_tag_pages.py --check

ruby scripts/audit-content.rb
ruby scripts/validate-curation.rb
ruby scripts/validate-tags.rb
bundle exec jekyll clean
TZ=UTC bundle exec jekyll build
ruby scripts/smoke-test.rb
python3 scripts/site-review.py
node scripts/search-interaction-test.js
node --check js/search.js
node --check js/pageContent.js
node --check js/tags.js
node --check js/toc.js
node --check js/main.js
node --check js/copy-code.js
ruby scripts/verify-post-history.rb
```

- `ruby scripts/audit-content.rb` reports the taxonomy audit and has a real exit status, which it previously did not — it always exited 0, so all the gates could stay green while the taxonomy drifted. It fails on a post with no title, a category absent from `topics.yml`, or a `display_title` that is *present but blank* (absent is fine: it is an optional override, and 240 posts omit it). "Suspicious" classifications and tag case variants are heuristics rather than verdicts, so they are **ratcheted** against baselines pinned at the top of the script and only fail when the count grows. Lower a baseline there after reviewing and fixing items.
- `ruby scripts/validate-curation.rb` checks front matter, curated source paths, reading-path references, editorial sidecar paths, topic IDs, and topic relations.
- `uv run --with-requirements scripts/requirements.txt scripts/generate_tag_pages.py --check` verifies that committed generated tag pages match the current front matter and slug data without rewriting them. The generator also writes `noindex: true` and `sitemap: false` into any tag page listing fewer than `TAG_NOINDEX_BELOW` (default 2) posts: 189 of 277 tag names are singletons, and those pages are reachable and still pass internal links, they just no longer compete in the index.
- `uv run --with-requirements scripts/requirements.txt scripts/generate_post_meta.py --check` verifies `_data/post_meta.yml` against the current posts. It resolves each post's language (declared `lang`, else inferred from the CJK share of its prose) and its reading statistics, and records a `reviewed` date only where one is traceable — an `updated` front-matter field or the latest `_data/format_fixes.yml` entry for that post. Never invent a review date; the project's own editorial policy treats metadata as descriptive, not evidence.
- `ruby scripts/validate-tags.rb` is read-only: it checks every active tag has a route and rejects unapproved slug collisions.
- `ruby scripts/smoke-test.rb` expects a successful build and checks generated routes, all source tag routes, sitemap/404, both JSON indexes, exact post/pagination counts, source notes, attribution, artifact exclusions, unresolved Liquid/empty links, a generated-site internal-link crawl, base-path URL wiring, and shipped JavaScript copies in `_site/`; set `SITE_DIR` when reviewing a non-default build destination.
- `scripts/smoke-test.rb` has a second section, "Content and metadata claims", that checks what the document *claims* rather than whether the repository is self-consistent: non-empty RSS descriptions and the required feed elements, agreement between `<html lang>`, `og:locale` and JSON-LD `inLanguage`, the sidecar against declared front matter, absence of duplicate structured data, cache-versioning on every CSS/JS reference, and absence of `http://` images. These exist because an RSS feed shipped 7 of 10 items with empty descriptions and 267 Chinese articles declared `lang="en"` while the whole pipeline stayed green; see `docs/review-2026-10-01.md`.
- `python3 scripts/site-review.py` checks rendered landmarks, headings, form-control names, current navigation state, external-link safety, and core shell markers; warnings identify historical-source exceptions without rewriting them.
- `node scripts/search-interaction-test.js` is a dependency-free regression for initial query loading and result rendering.
- `python3 scripts/sync_upstream.py` writes post bodies from the cnblogs export into `_posts/`. Dry run by default; `--execute` to write. Bodies only — never front matter, filenames or dates, so no published URL moves. Three classes are never touched because overwriting them would destroy work rather than sync it: the 19 `curated: true` posts (net-new, no upstream source), the merged `llm-probe` post (Blog Garden received it as two parts under its 200 KB cap), and the 7 export files with no public URL (importing them would publish them). It also refuses an empty upstream body when the post is not empty — 326 of 337 paired exports have no front matter at all, and an early version of the loader returned `""` for those and would have blanked 326 articles. Idempotent: re-running reports 0.
- **`upstream_sync: off` in a post's front matter means this repository is the source for that post, and `sync_upstream.py` will not write it.** Six posts carry it, each with an `upstream_sync_reason` giving the evidence. This is the mechanism; the date rule below is only the fallback for posts with no explicit statement. Mark a post when cnblogs holds something worse than here, which is not always the era a post belongs to: `2024-08-15-Code-C++-regex.md` is a 2024 post that cnblogs had reduced to 101 characters of syntactically invalid C++, while `2026-09-05-New-API-Multi-Process-Docker.md` carries an upstream-absent erratum withdrawing a withdrawn deployment design.
- **The content flow reverses at 2026-06, and it reverses inconsistently.** Before that date every article was imported from cnblogs, so cnblogs is the source and syncing is unambiguously forward (295 paired posts: 42 identical, 174 behind, **0 ahead**). From 2026-06 editing happens here and publishes outward (42 paired: 17 identical, 14 behind, **1 ahead**, 2 marked on both sides). `2026-09-05-New-API-Multi-Process-Docker.md` is that one ahead — it carries an upstream-absent `重要勘误（2026-09-25）` withdrawing the old built-in-worker design — so the sync reports that era for review and writes none of it. Do not "fix" the date threshold to make the count zero.
- `scripts/upstream_text.py` is the single definition of "synced": the normaliser, this repository's corrections, and `expected_body()`. `compare_upstream.py` and `sync_upstream.py` both call it. They each carried their own copy for a while and disagreed — the report called 90 articles drifted right after a clean sync, then 68, because it did not know about `%20` link targets, repaired empty-target links, or re-applied `format_fixes.yml` rewrites, and then used strict equality where the writer used typographic equivalence. Keep one copy.
- Corrections derived from text are re-derived on every sync (`repair_broken_links`, `encode_link_target_whitespace`), so they cannot be lost to an upstream copy a second time. Two of them already were: `书签中的一些工具整理` and `吾爱破解-培训第一课` were fixed on 2026-09-25 and lost again on 2026-10-01 because cnblogs still holds the defective form. Corrections *not* derivable from the text carry a `rewrite:` rule in `format_fixes.yml` instead (the meldmerge https upgrade). Note that encoding a space in a link target makes the href legal but does not make the link resolve — that PEiD URL answers 404 either way.
- `python3 scripts/compare_upstream.py` compares the cnblogs export (the source of truth) against `_posts/`. Use it after re-exporting upstream, or before publishing, to see what the two sides disagree on. A plain hash diff is useless here: the import is deliberately lossy, so normalising whitespace alone reports 356 of 357 posts as changed. The script normalises the four transformations the importer performs on purpose and classifies the rest into *identical*, *covered by format_fixes.yml*, *upstream-declaration-only*, *spacing-only* and *substantive*. It exits non-zero only on substantive differences. Measured before the sync on 2026-10-01 that was 248 of 331 matched articles, 27 of them showing version facts at values upstream had corrected; after `sync_upstream.py` ran it is **0**, with 19 held for review because the flow reverses there. See `docs/review-2026-10-01.md` §9 and §10.
- `ruby scripts/verify-post-history.rb` compares the 331 pre-curation post blobs; it allows new posts and only the explicit, blob-bound exceptions in `_data/format_fixes.yml`, rejecting other baseline edits/deletions.
- CI uses Ruby 3.2, provisions uv, runs the explicit Python tag-generator dependency through `uv run`, checks generated tag-page consistency, and runs a clean build, curation validation, smoke tests, JavaScript syntax checks, and a baseline-aware historical-post blob check before Pages deployment; see `.github/workflows/pages.yml`.
- Historical articles may contain excerpt/Liquid syntax or evidence-backed safety corrections that must be recorded in `_data/format_fixes.yml`; never hide a new warning by weakening the build.
- **`timezone: UTC` in `_config.yml` is load-bearing, not decoration.** The permalink is derived from each post's front-matter date, and Jekyll reads a naive `date:` in the build machine's zone. 78 of the 357 posts carry a time between 00:00 and 08:00 local, so without this line a build running in Asia/Shanghai moves those 78 URLs back one day while CI — which sets `TZ: UTC` — publishes the correct ones. Local previews then disagree with production for a fifth of the archive. Do not change it to a local zone: that would move 78 live URLs. `smoke-test.rb` fails if it is removed or if the sitemap's date multiset stops matching the front matter.
- Changes to `_config.yml` require restarting `jekyll serve`; GitHub Pages builds with the Pages base path, so avoid hard-coded root-relative links in templates or JavaScript.

## Cross-domain and privacy notes

- **Both domains are live and self-canonical.** `www.cnblogs.com/yongchao/p/<postId>.html`
  and the equivalent `https://blog.wyclswq.top/...` article are both reachable. Neither
  side declares a canonical to the other and neither is `noindex`, so the same article is
  indexable on two domains with competing canonical signals. This is a known open item,
  not an oversight to be silently "fixed" in a template — it needs a one-time decision
  about which domain is authoritative going forward, and cnblogs does not expose a
  free-tier per-post canonical tag, so it likely needs a migration/redirect plan.
- **`_drafts/` is tracked in git, so its contents are in public history.** The directory
  currently holds personal material (private diary entries, a team-building retrospective)
  that is deliberately unpublished. Jekyll never builds `_drafts/`, but git has no notion
  of "private": everything there is in every clone, in GitHub code search, and
  archivable by third parties. Do not add personal or pre-publication material to this
  repository. Removing what is already committed requires rewriting history, and that
  cannot recall existing clones — treat it as a one-way decision, not a routine edit.

## Safe workflow

- Start with `git status --short`; this repository may contain a large uncommitted editorial/design phase.
- Prefer sidecar YAML and new pages over rewriting or moving historical articles. If deleting or merging content, first identify inbound links and preserve a redirect/archive strategy where practical.
- After a successful build, inspect the generated homepage, `/start-here/`, `/curated/`, one topic page, `/archive/`, `/search/`, and the generated JSON indexes.
- Do not commit or push unless the user explicitly requests it. Pushing `master` triggers the Pages workflow.
- Read `docs/content-optimization.md` for the content baseline and `docs/technical-review-2026-09-25.md` for the latest external technical cross-checks.

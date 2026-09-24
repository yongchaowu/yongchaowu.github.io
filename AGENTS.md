# Agent notes

## Repository shape

- This is a Jekyll 4 site deployed to GitHub Pages; there is no Node/package-manager test suite.
- `_posts/` contains the published Markdown articles. `permalink: /:year/:month/:day/:title/` is part of the public URL contract.
- `page/` contains utility pages; `topics/` contains thin topic pages; `_layouts/`, `_includes/`, and `_sass/` implement the site shell and presentation.
- `_data/` is the editorial source of truth: `navigation.yml`, `reading_paths.yml`, `topics.yml`, `post_editorial.yml`, `topic_relations.yml`, `tag_aliases.yml`, `featured_tags.yml`, and the explicit `format_fixes.yml` exception list.
- `post_editorial.yml` stores `posts` as a list of records; Liquid consumers must not treat it as a hash of key/value records.
- `search.json` and `posts-meta.json` are Liquid source templates, not hand-maintained generated data. `_site/` is ignored build output; never edit it.
- `scripts/` is repository tooling and is intentionally excluded from the public Pages artifact.

## Content and URL rules

- Preserve historical source files, dates, bodies, and generated post URLs unless the user explicitly asks for a destructive migration. If historical edits are intentional, record formatting-only exceptions in `_data/format_fixes.yml` and update URL/reference audits in the same change.
- The curated layer is additive: curated posts use `curated: true`, `content_origin: curated`, `summary`, `lang`, and repository-relative `source_posts`; validate every source path.
- Editorial metadata is descriptive, not evidence. Do not call a note independently verified/current/authoritative unless the repository or an attached source supports that claim; keep version-sensitive, AI-assisted, imported, historical, and unverified states visible.
- Use `relative_url` for internal links. Keep the canonical routes `/`, `/pageN/`, `/curated/`, `/category/`, `/archive/`, `/tag/`, `/tag/<slug>/`, `/search/`, and `/about/` compatible.
- Do not create `tag/index.md`: `page/2tags.html` is the intentional canonical `/tag/` page and duplicate permalinks break Jekyll.

## Build and verification

Run from the repository root. The local Bundler is vendored; use `bundle exec`.

```bash
# Only needed after changing post tags or tag slug data:
python3 scripts/generate_tag_pages.py

ruby scripts/audit-content.rb
ruby scripts/validate-curation.rb
ruby scripts/validate-tags.rb
bundle exec jekyll clean
TZ=UTC bundle exec jekyll build
ruby scripts/smoke-test.rb
node --check js/search.js
node --check js/pageContent.js
node --check js/tags.js
node --check js/toc.js
node --check js/main.js
node --check js/copy-code.js
ruby scripts/verify-post-history.rb
```

- `ruby scripts/validate-curation.rb` checks front matter, curated source paths, reading-path references, editorial sidecar paths, topic IDs, and topic relations.
- `ruby scripts/validate-tags.rb` is read-only: it checks every active tag has a route and rejects unapproved slug collisions.
- `ruby scripts/smoke-test.rb` expects a successful build and checks generated routes, both JSON indexes, exact post/pagination counts, source notes, artifact exclusions, unresolved Liquid/empty links, base-path URL wiring, and shipped JavaScript copies in `_site/`.
- `ruby scripts/verify-post-history.rb` compares the 331 pre-curation post blobs; it allows new posts and only the explicit formatting exceptions in `_data/format_fixes.yml`, rejecting other baseline edits/deletions.
- CI uses Ruby 3.2 and runs a clean build, curation validation, smoke tests, JavaScript syntax checks, and a baseline-aware historical-post blob check before Pages deployment; see `.github/workflows/pages.yml`.
- Historical articles may contain excerpt/Liquid syntax that must be fixed through `_data/format_fixes.yml`; never hide a new warning by weakening the build.
- Changes to `_config.yml` require restarting `jekyll serve`; GitHub Pages builds with the Pages base path, so avoid hard-coded root-relative links in templates or JavaScript.

## Safe workflow

- Start with `git status --short`; this repository may contain a large uncommitted editorial/design phase.
- Prefer sidecar YAML and new pages over rewriting or moving historical articles. If deleting or merging content, first identify inbound links and preserve a redirect/archive strategy where practical.
- After a successful build, inspect the generated homepage, `/start-here/`, `/curated/`, one topic page, `/archive/`, `/search/`, and the generated JSON indexes.
- Do not commit or push unless the user explicitly requests it. Pushing `master` triggers the Pages workflow.
- Read `docs/content-optimization.md` for the content baseline, provenance rules, and known taxonomy/version warnings.

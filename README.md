# yongchaowu.github.io

Personal blog of **Yc.W (@yongchao)** — <https://www.wyclswq.top>

Tech notes on C++, OS, tools, and AI/LLM deployment, migrated from my cnblogs blog [Theseus'Ship](https://www.cnblogs.com/yongchao/).

- Jekyll + GitHub Pages, theme based on [HyG's](https://github.com/Gaohaoyang/gaohaoyang.github.io)
- Curated, non-destructive reading layer: [`/curated/`](https://www.wyclswq.top/curated/) (19 curated guides/deep dives)
- Content policy and audit notes: [`docs/content-optimization.md`](docs/content-optimization.md)
- Build locally: `bundle exec jekyll serve`
- Validate curated source links: `ruby scripts/validate-curation.rb`
- Validate tag routes and collisions: `ruby scripts/validate-tags.rb`
- Check generated tag pages with `uv run --with-requirements scripts/requirements.txt scripts/generate_tag_pages.py --check`
- Review rendered site controls and landmarks: `python3 scripts/site-review.py`
- Verify historical post blobs: `ruby scripts/verify-post-history.rb`
- Run generated-site smoke tests: `ruby scripts/smoke-test.rb`

#!/usr/bin/env python3
"""
Generate static tag pages from post front matter.

Reads _data/tag_slugs.yml for explicit slug overrides and writes
 tag/<slug>/index.md files. Use --check in CI to verify that committed
 generated pages exactly match the current post/tag inputs without writing.
"""
import argparse
import os
import re
import sys
from collections import defaultdict

try:
    import yaml
except ModuleNotFoundError:
    print(
        "PyYAML is required. Run this script with: "
        "uv run --with-requirements scripts/requirements.txt scripts/generate_tag_pages.py",
        file=sys.stderr,
    )
    sys.exit(2)

POSTS_DIR = '_posts'
SLUGS_FILE = '_data/tag_slugs.yml'
OUTPUT_DIR = 'tag'


def load_slug_overrides():
    with open(SLUGS_FILE, 'r', encoding='utf-8') as handle:
        return yaml.safe_load(handle) or {}


def slugify(tag_name):
    """Convert tag name to URL-safe slug."""
    tag_name = str(tag_name)
    slug = tag_name.lower()
    # Keep Chinese characters, alphanumeric, and hyphens.
    slug = re.sub(r'[^\w\u4e00-\u9fff]+', '-', slug)
    slug = re.sub(r'^-|-$', '', slug)
    if not slug:
        slug = re.sub(r'[^\w\u4e00-\u9fff]', '', tag_name.lower())
    return slug


def parse_front_matter(filepath):
    """Extract a front-matter mapping from a Markdown file."""
    with open(filepath, 'r', encoding='utf-8') as handle:
        content = handle.read()

    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}

    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as error:
        print(f'ERROR: invalid front matter in {filepath}: {error}', file=sys.stderr)
        return {}


def collect_tags():
    """Collect all tags and their post counts."""
    tag_posts = defaultdict(list)
    slug_overrides = load_slug_overrides()
    slugs_used = {}

    for filename in sorted(os.listdir(POSTS_DIR)):
        if not filename.endswith('.md'):
            continue
        filepath = os.path.join(POSTS_DIR, filename)
        tags = parse_front_matter(filepath).get('tags', []) or []

        for tag in tags:
            tag = str(tag)
            slug = str(slug_overrides.get(tag, slugify(tag)))
            slug_lower = slug.lower()
            if slug_lower in slugs_used and slugs_used[slug_lower].lower() != tag.lower():
                print(
                    f"ERROR: Slug collision: '{tag}' and "
                    f"'{slugs_used[slug_lower]}' both map to '{slug}'",
                    file=sys.stderr,
                )
                sys.exit(1)
            slugs_used[slug_lower] = tag
            tag_posts[(tag, slug)].append(filename)

    return tag_posts


def render_tag_page(tag, slug):
    """Return the complete generated page content."""
    return f'''---
layout: tag
title: "{tag}"
tag: "{tag}"
slug: "{slug}"
permalink: /tag/{slug}/
generated: true
---
'''


def generate_tag_page(tag, slug, output_dir=OUTPUT_DIR):
    """Generate a single tag page and return its path."""
    os.makedirs(os.path.join(output_dir, slug), exist_ok=True)
    output_path = os.path.join(output_dir, slug, 'index.md')
    with open(output_path, 'w', encoding='utf-8') as handle:
        handle.write(render_tag_page(tag, slug))
    return output_path


def expected_tag_pages(tag_posts, output_dir=OUTPUT_DIR):
    """Return expected generated page contents keyed by path.

    Sorting mirrors the normal generation loop. When case variants share a
    slug, the last sorted label is the deterministic page label.
    """
    expected = {}
    for (tag, slug) in sorted(tag_posts):
        expected[os.path.join(output_dir, slug, 'index.md')] = render_tag_page(tag, slug)
    return expected


def generated_tag_pages(output_dir=OUTPUT_DIR):
    """Return paths of committed pages marked as generated."""
    paths = set()
    for path in sorted(os.listdir(output_dir)) if os.path.isdir(output_dir) else []:
        page_path = os.path.join(output_dir, path, 'index.md')
        if os.path.isfile(page_path) and parse_front_matter(page_path).get('generated') is True:
            paths.add(page_path)
    return paths


def check_generated_pages(tag_posts, output_dir=OUTPUT_DIR):
    """Check committed generated pages without modifying the working tree."""
    expected = expected_tag_pages(tag_posts, output_dir)
    actual = generated_tag_pages(output_dir)
    errors = []

    missing = sorted(set(expected) - actual)
    stale = sorted(actual - set(expected))
    if missing:
        errors.append(f'missing generated pages: {len(missing)}')
    if stale:
        errors.append(f'stale generated pages: {len(stale)}')

    mismatched = []
    for path in sorted(set(expected) & actual):
        with open(path, 'r', encoding='utf-8') as handle:
            if handle.read() != expected[path]:
                mismatched.append(path)
    if mismatched:
        errors.append(f'content mismatches: {len(mismatched)}')

    if errors:
        print('Tag page consistency: FAIL', file=sys.stderr)
        for error in errors:
            print(f'  - {error}', file=sys.stderr)
        for path in (missing + stale + mismatched)[:10]:
            print(f'    {path}', file=sys.stderr)
        return False

    print(f'Tag page consistency: PASS ({len(expected)} generated pages)')
    return True


def generate_tag_index(tag_posts):
    """Return the existing server-rendered tag index path.

    The site uses page/2tags.html as the canonical /tag/ page. Generating
    a second Markdown page with the same permalink causes a Jekyll destination
    conflict, so this function intentionally does not write tag/index.md.
    """
    del tag_posts
    return os.path.join(OUTPUT_DIR, 'index.html')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--check',
        action='store_true',
        help='verify committed generated pages without changing files',
    )
    args = parser.parse_args()

    print('Collecting tags from posts...')
    tag_posts = collect_tags()
    print(f'Found {len(tag_posts)} unique tags')

    if args.check:
        return 0 if check_generated_pages(tag_posts) else 1

    for (tag, slug), posts in sorted(tag_posts.items()):
        path = generate_tag_page(tag, slug)
        print(f'  {tag} -> /tag/{slug}/ ({len(posts)} posts)')

    generate_tag_index(tag_posts)
    print('\nTag index is provided by page/2tags.html; no duplicate index was written.')
    print('Done!')
    return 0


if __name__ == '__main__':
    sys.exit(main())

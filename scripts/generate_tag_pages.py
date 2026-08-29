#!/usr/bin/env python3
"""
Generate static tag pages from post front matter.
Reads _data/tag_slugs.yml for explicit slug overrides.
Outputs tag/<slug>/index.md files.
"""
import os
import re
import sys
import yaml
from collections import defaultdict

POSTS_DIR = '_posts'
SLUGS_FILE = '_data/tag_slugs.yml'
OUTPUT_DIR = 'tag'

def load_slug_overrides():
    with open(SLUGS_FILE, 'r') as f:
        return yaml.safe_load(f) or {}

def slugify(tag_name):
    """Convert tag name to URL-safe slug."""
    slug = tag_name.lower()
    # Keep Chinese characters, alphanumeric, and hyphens
    slug = re.sub(r'[^\w\u4e00-\u9fff]+', '-', slug)
    slug = re.sub(r'^-|-$', '', slug)
    if not slug:
        slug = re.sub(r'[^\w\u4e00-\u9fff]', '', tag_name.lower())
    return slug

def parse_front_matter(filepath):
    """Extract tags from post front matter."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find front matter
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return []

    try:
        fm = yaml.safe_load(match.group(1))
        if fm and 'tags' in fm:
            return fm['tags']
    except yaml.YAMLError:
        pass
    return []

def collect_tags():
    """Collect all tags and their post counts."""
    tag_posts = defaultdict(list)
    slug_overrides = load_slug_overrides()
    slugs_used = {}

    for filename in sorted(os.listdir(POSTS_DIR)):
        if not filename.endswith('.md'):
            continue
        filepath = os.path.join(POSTS_DIR, filename)
        tags = parse_front_matter(filepath)

        for tag in tags:
            # Get slug
            if tag in slug_overrides:
                slug = slug_overrides[tag]
            else:
                slug = slugify(tag)

            # Check for slug collision (case-insensitive)
            slug_lower = slug.lower()
            if slug_lower in slugs_used and slugs_used[slug_lower] != tag:
                # Allow case-insensitive duplicates if they map to the same slug
                if slug.lower() != slugs_used[slug_lower].lower():
                    print(f"ERROR: Slug collision: '{tag}' and '{slugs_used[slug_lower]}' both map to '{slug}'", file=sys.stderr)
                    sys.exit(1)
            slugs_used[slug_lower] = tag

            tag_posts[(tag, slug)].append(filename)

    return tag_posts

def generate_tag_page(tag, slug, posts):
    """Generate a single tag page."""
    os.makedirs(os.path.join(OUTPUT_DIR, slug), exist_ok=True)

    post_list = '\n'.join([f'  - {p}' for p in posts])

    content = f"""---
layout: tag
title: "{tag}"
tag: "{tag}"
slug: "{slug}"
permalink: /tag/{slug}/
generated: true
---
"""
    output_path = os.path.join(OUTPUT_DIR, slug, 'index.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return output_path

def generate_tag_index(tag_posts):
    """Generate the /tag/ index page."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Sort tags by post count (descending)
    sorted_tags = sorted(tag_posts.items(), key=lambda x: -len(x[1]))

    tag_lines = []
    for (tag, slug), posts in sorted_tags:
        tag_lines.append(f'  - name: "{tag}"')
        tag_lines.append(f'    slug: "{slug}"')
        tag_lines.append(f'    count: {len(posts)}')

    content = f"""---
layout: tag_index
title: Tags
permalink: /tag/
generated: true
---
"""
    output_path = os.path.join(OUTPUT_DIR, 'index.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return output_path

def main():
    print("Collecting tags from posts...")
    tag_posts = collect_tags()
    print(f"Found {len(tag_posts)} unique tags")

    # Generate individual tag pages
    for (tag, slug), posts in sorted(tag_posts.items()):
        path = generate_tag_page(tag, slug, posts)
        print(f"  {tag} -> /tag/{slug}/ ({len(posts)} posts)")

    # Generate tag index
    index_path = generate_tag_index(tag_posts)
    print(f"\nGenerated tag index: {index_path}")
    print("Done!")

if __name__ == '__main__':
    main()

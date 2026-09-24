#!/usr/bin/env ruby
# frozen_string_literal: true

# Read-only tag catalog audit. It does not generate or delete tag pages.
# Usage: ruby scripts/validate-tags.rb

require 'yaml'
require 'date'

ROOT = File.expand_path('..', __dir__)
POSTS_DIR = File.join(ROOT, '_posts')
SLUGS_FILE = File.join(ROOT, '_data', 'tag_slugs.yml')
ALIASES_FILE = File.join(ROOT, '_data', 'tag_aliases.yml')

def load_data(path)
  YAML.safe_load_file(path, permitted_classes: [Date, Time], aliases: false) || {}
end

slug_overrides = load_data(SLUGS_FILE)
aliases = load_data(ALIASES_FILE).fetch('aliases', {})

def front_matter(path)
  content = File.read(path, encoding: 'UTF-8')
  match = content.match(/\A---\s*\n(.*?)\n---\s*\n/m)
  return {} unless match

  YAML.safe_load(match[1], permitted_classes: [Date, Time], aliases: false) || {}
rescue Psych::Exception
  {}
end

def slugify(value)
  value = value.to_s.downcase
  value = value.gsub(/[^\p{L}\p{N}_-]+/u, '-').gsub(/\A-+|-+\z/, '')
  value.empty? ? value.to_s.downcase.gsub(/[^\p{L}\p{N}_-]+/u, '') : value
end

def route_exists?(root, slug)
  File.file?(File.join(root, 'tag', slug, 'index.md'))
end

errors = []
tags_by_slug = Hash.new { |hash, key| hash[key] = [] }
Dir.glob(File.join(POSTS_DIR, '*.md')).sort.each do |path|
  data = front_matter(path)
  Array(data['tags']).each do |tag|
    name = tag.to_s
    slug = (slug_overrides[name] || slugify(name)).to_s
    tags_by_slug[slug] << name unless tags_by_slug[slug].include?(name)
  end
end

tags_by_slug.each do |slug, names|
  errors << "missing tag page for #{names.join(' / ')}: #{slug}" unless route_exists?(ROOT, slug)

  next if names.length < 2

  normalized = names.map(&:downcase).uniq
  alias_ok = names.all? do |name|
    target = aliases[name]
    target.is_a?(String) && names.include?(target)
  end
  errors << "ambiguous slug #{slug}: #{names.join(' / ')}" unless normalized.length == 1 || alias_ok
end

active_tag_names = tags_by_slug.values.flatten
Dir.glob(File.join(ROOT, 'tag', '*', 'index.md')).sort.each do |page_path|
  data = front_matter(page_path)
  next unless data['generated'] == true

  slug = File.basename(File.dirname(page_path))
  tag_name = data['tag'].to_s
  errors << "stale generated tag page: #{slug} (#{tag_name})" unless active_tag_names.include?(tag_name)
  errors << "generated tag slug mismatch: #{slug}" unless data['slug'].to_s == slug
  errors << "generated tag permalink mismatch: #{slug}" unless data['permalink'].to_s == "/tag/#{slug}/"
end

featured_file = File.join(ROOT, '_data', 'featured_tags.yml')
featured = load_data(featured_file).fetch('tags', [])
featured.each do |tag|
  errors << "featured tag has no posts: #{tag}" unless tags_by_slug.values.flatten.include?(tag.to_s)
end

puts "Active tag slugs: #{tags_by_slug.length}"
puts "Active tag names: #{tags_by_slug.values.flatten.length}"
puts "Featured tags checked: #{featured.length}"
if errors.empty?
  puts 'Tag catalog validation: PASS'
  exit 0
end

warn "Tag catalog validation: FAIL (#{errors.length} issue#{'s' unless errors.length == 1})"
errors.each { |error| warn "  - #{error}" }
exit 1

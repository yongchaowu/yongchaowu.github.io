#!/usr/bin/env ruby
# frozen_string_literal: true

# Validate the non-destructive curated layer without rewriting historical posts.
# Usage: ruby scripts/validate-curation.rb

require 'yaml'

POSTS_DIR = File.expand_path('../_posts', __dir__)
TOPICS_FILE = File.expand_path('../_data/topics.yml', __dir__)

def front_matter(path)
  content = File.read(path, encoding: 'UTF-8')
  match = content.match(/\A---\s*\n(.*?)\n---\s*\n/m)
  return {} unless match

  YAML.safe_load(match[1], permitted_classes: [Time], aliases: false) || {}
rescue Psych::Exception => e
  warn "#{path}: invalid YAML: #{e.message}"
  {}
end

posts = Dir.glob(File.join(POSTS_DIR, '*.md')).sort
repo_root = File.expand_path('..', __dir__)
posts_root = File.expand_path(POSTS_DIR)
canonical_topics = YAML.load_file(TOPICS_FILE).fetch('topics').map { |topic| topic['name'] }
errors = []
curated = []

posts.each do |path|
  basename = File.basename(path)
  data = front_matter(path)
  title = data['title'].to_s.strip
  categories = Array(data['categories'])
  tags = Array(data['tags'])

  errors << "#{basename}: missing title" if title.empty?
  errors << "#{basename}: missing canonical category" if categories.empty? || !canonical_topics.include?(categories.first)
  errors << "#{basename}: tags must be an array" unless tags.is_a?(Array)

  next unless data['curated']

  curated << basename
  errors << "#{basename}: curated post needs a summary" if data['summary'].to_s.strip.empty?
  errors << "#{basename}: curated post needs a language" if data['lang'].to_s.strip.empty?
  errors << "#{basename}: curated post must declare content_origin: curated" unless data['content_origin'] == 'curated'

  sources = Array(data['source_posts'])
  errors << "#{basename}: curated post needs source_posts" if sources.empty?
  body = File.read(path, encoding: 'UTF-8').split(/^---\s*$\n/, 3).last.to_s
  errors << "#{basename}: raw _posts link in body" if body.include?('](_posts/')
  sources.each do |source|
    source_name = source.to_s.sub(%r{\A\./}, '')
    source_path = File.expand_path(source_name, repo_root)
    source_basename = File.basename(source_name)
    unless source_path.start_with?("#{posts_root}#{File::SEPARATOR}")
      errors << "#{basename}: source path escapes _posts: #{source_name}"
      next
    end
    errors << "#{basename}: source path does not exist: #{source_name}" unless File.file?(source_path)
    errors << "#{basename}: malformed inline source link for #{source_basename}" if body.include?("](#source-posts-title)#{source_basename})")
  end
end

puts "Total posts: #{posts.length}"
puts "Historical originals: #{posts.length - curated.length}"
puts "Curated posts: #{curated.length}"
puts "Source links checked: #{curated.sum { |name| Array(front_matter(File.join(POSTS_DIR, name))['source_posts']).length }}"
puts

if errors.empty?
  puts 'Curation validation: PASS'
  exit 0
end

warn "Curation validation: FAIL (#{errors.length} issue#{'s' unless errors.length == 1})"
errors.each { |error| warn "  - #{error}" }
exit 1

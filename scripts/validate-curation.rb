#!/usr/bin/env ruby
# frozen_string_literal: true

# Validate the non-destructive curated layer without rewriting historical posts.
# Usage: ruby scripts/validate-curation.rb

require 'yaml'

POSTS_DIR = File.expand_path('../_posts', __dir__)
TOPICS_FILE = File.expand_path('../_data/topics.yml', __dir__)
EDITORIAL_FILE = File.expand_path('../_data/post_editorial.yml', __dir__)
READING_PATHS_FILE = File.expand_path('../_data/reading_paths.yml', __dir__)
RELATIONS_FILE = File.expand_path('../_data/topic_relations.yml', __dir__)

def front_matter(path)
  content = File.read(path, encoding: 'UTF-8')
  match = content.match(/\A---\s*\n(.*?)\n---\s*\n/m)
  return {} unless match

  YAML.safe_load(match[1], permitted_classes: [Time], aliases: false) || {}
rescue Psych::Exception => e
  warn "#{path}: invalid YAML: #{e.message}"
  {}
end

def source_file_exists?(source, repo_root, posts_root)
  source_path = File.expand_path(source.to_s.sub(%r{\A\./}, ''), repo_root)
  source_path.start_with?("#{posts_root}#{File::SEPARATOR}") && File.file?(source_path)
end

posts = Dir.glob(File.join(POSTS_DIR, '*.md')).sort
repo_root = File.expand_path('..', __dir__)
posts_root = File.expand_path(POSTS_DIR)
canonical_topics = YAML.load_file(TOPICS_FILE).fetch('topics').map { |topic| topic['name'] }
errors = []
curated = []
curated_paths = Hash.new(0)

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
  curated_paths["_posts/#{basename}"] += 1
  errors << "#{basename}: curated post needs a summary" if data['summary'].to_s.strip.empty?
  errors << "#{basename}: curated post needs a language" if data['lang'].to_s.strip.empty?
  errors << "#{basename}: curated post must declare content_origin: curated" unless data['content_origin'] == 'curated'
  allowed_curation_levels = %w[roadmap deep-dive runbook tutorial reference lab-guide editorial]
  errors << "#{basename}: unsupported curation_level #{data['curation_level']}" unless allowed_curation_levels.include?(data['curation_level'])

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

editorial_data = YAML.load_file(EDITORIAL_FILE)
reading_paths_data = YAML.load_file(READING_PATHS_FILE)
relations_data = YAML.load_file(RELATIONS_FILE)
canonical_topic_ids = YAML.load_file(TOPICS_FILE).fetch('topics').map { |topic| topic['id'] }
editorial_entries = editorial_data.fetch('posts', [])
errors << 'editorial posts must be an array' unless editorial_entries.is_a?(Array)
editorial_entries = [] unless editorial_entries.is_a?(Array)
editorial_ids = Hash.new(0)
editorial_paths = Hash.new(0)
allowed_verifications = %w[unknown editorial-review reported-tested not-tested review-required]
allowed_freshness = %w[historical current version-sensitive]
editorial_entries.each do |item|
  unless item.is_a?(Hash)
    errors << 'editorial entry must be a mapping'
    next
  end

  key = item['id'] || item['post']
  source = item['post']
  editorial_ids[item['id']] += 1 unless item['id'].to_s.empty?
  editorial_paths[source] += 1 unless source.to_s.empty?
  errors << "editorial #{key}: missing id" if item['id'].to_s.empty?
  errors << "editorial #{key}: missing post path" if source.to_s.empty?
  errors << "editorial #{key}: post path does not exist: #{source}" unless source_file_exists?(source, repo_root, posts_root)
  primary = item['primary_topic']
  errors << "editorial #{key}: unknown primary topic #{primary}" if primary && !canonical_topic_ids.include?(primary)
  errors << "editorial #{key}: unsupported verification #{item['verification']}" unless allowed_verifications.include?(item['verification'])
  errors << "editorial #{key}: unsupported freshness #{item['freshness']}" unless allowed_freshness.include?(item['freshness'])
  Array(item['secondary_topics']).each do |secondary|
    errors << "editorial #{key}: unknown secondary topic #{secondary}" unless canonical_topic_ids.include?(secondary)
  end
end
editorial_ids.each do |id, count|
  errors << "editorial id #{id} is duplicated #{count} times" if count > 1
end
editorial_paths.each do |path, count|
  errors << "editorial post #{path} is duplicated #{count} times" if count > 1
end
curated_paths.each do |path, count|
  errors << "curated post #{path} needs exactly one editorial record" unless editorial_paths[path] == 1
end


reading_paths_data.fetch('paths', []).each do |path|
  errors << "reading path #{path['id']}: missing outcome" if path['outcome'].to_s.strip.empty?
  errors << "reading path #{path['id']}: estimated_minutes must be positive" unless path['estimated_minutes'].to_s.to_i.positive?
  errors << "reading path #{path['id']}: prerequisites must be an array" unless path['prerequisites'].is_a?(Array)
  Array(path['posts']).each do |source|
    errors << "reading path #{path['id']}: post path does not exist: #{source}" unless source_file_exists?(source, repo_root, posts_root)
  end
end

YAML.load_file(TOPICS_FILE).fetch('topics').each do |topic|
  Array(topic['featured_posts']).each do |source|
    errors << "topic #{topic['id']}: featured post does not exist: #{source}" unless source_file_exists?(source, repo_root, posts_root)
  end
end

relations_data.fetch('relations', []).each do |relation|
  errors << "topic relation: unknown from topic #{relation['from']}" unless canonical_topic_ids.include?(relation['from'])
  errors << "topic relation: unknown to topic #{relation['to']}" unless canonical_topic_ids.include?(relation['to'])
end

puts "Total posts: #{posts.length}"
puts "Historical originals: #{posts.length - curated.length}"
puts "Curated posts: #{curated.length}"
puts "Source links checked: #{curated.sum { |name| Array(front_matter(File.join(POSTS_DIR, name))['source_posts']).length }}"
puts "Editorial sidecars: #{editorial_entries.length}"
puts "Reading paths: #{reading_paths_data.fetch('paths', []).length}"
puts

if errors.empty?
  puts 'Curation validation: PASS'
  exit 0
end

warn "Curation validation: FAIL (#{errors.length} issue#{'s' unless errors.length == 1})"
errors.each { |error| warn "  - #{error}" }
exit 1

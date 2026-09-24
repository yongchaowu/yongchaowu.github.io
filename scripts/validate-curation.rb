#!/usr/bin/env ruby
# frozen_string_literal: true

# Validate the non-destructive curated layer without rewriting historical posts.
# Usage: ruby scripts/validate-curation.rb

require 'yaml'
require 'date'

POSTS_DIR = File.expand_path('../_posts', __dir__)
TOPICS_FILE = File.expand_path('../_data/topics.yml', __dir__)
EDITORIAL_FILE = File.expand_path('../_data/post_editorial.yml', __dir__)
READING_PATHS_FILE = File.expand_path('../_data/reading_paths.yml', __dir__)
RELATIONS_FILE = File.expand_path('../_data/topic_relations.yml', __dir__)

def load_data(path)
  YAML.safe_load_file(path, permitted_classes: [Date, Time], aliases: false) || {}
end

def front_matter(path)
  content = File.read(path, encoding: 'UTF-8')
  match = content.match(/\A---\s*\n(.*?)\n---\s*\n/m)
  return {} unless match

  YAML.safe_load(match[1], permitted_classes: [Date, Time], aliases: false) || {}
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
canonical_topics = load_data(TOPICS_FILE).fetch('topics').map { |topic| topic['name'] }
errors = []
curated = []
curated_paths = Hash.new(0)
citation_count = 0

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
  citation_targets = body.scan(/\]\(#source-note-(\d+)\)/).flatten.map(&:to_i)
  citation_count += citation_targets.length
  citation_targets.each do |target|
    errors << "#{basename}: citation target ##{target} is outside source_posts" unless target.between?(1, sources.length)
  end
  errors << "#{basename}: citation still points to the aggregate source heading" if body.include?('](#source-posts-title)')
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

editorial_data = load_data(EDITORIAL_FILE)
reading_paths_data = load_data(READING_PATHS_FILE)
relations_data = load_data(RELATIONS_FILE)
canonical_topic_ids = load_data(TOPICS_FILE).fetch('topics').map { |topic| topic['id'] }
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

  attribution = item['attribution']
  if attribution
    unless attribution.is_a?(Hash)
      errors << "editorial #{key}: attribution must be a mapping"
    else
      %w[author source_url license license_status attribution_basis].each do |field|
        errors << "editorial #{key}: attribution missing #{field}" if attribution[field].to_s.strip.empty?
      end
      source_url = attribution['source_url'].to_s
      errors << "editorial #{key}: attribution source_url must be HTTPS" unless source_url.start_with?('https://')
      license_url = attribution['license_url'].to_s
      if !license_url.empty? && !license_url.start_with?('https://')
        errors << "editorial #{key}: attribution license_url must be HTTPS"
      end
      allowed_license_statuses = %w[declared-in-source partial-source-review not-verified]
      errors << "editorial #{key}: unsupported attribution license_status #{attribution['license_status']}" unless allowed_license_statuses.include?(attribution['license_status'])
    end
  elsif item['origin'] == 'imported'
    errors << "editorial #{key}: imported source needs attribution metadata"
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

load_data(TOPICS_FILE).fetch('topics').each do |topic|
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
puts "Attribution records: #{editorial_entries.count { |item| item.is_a?(Hash) && item['attribution'] }}"
puts "Claim-level citation links: #{citation_count}"
puts "Reading paths: #{reading_paths_data.fetch('paths', []).length}"
puts

if errors.empty?
  puts 'Curation validation: PASS'
  exit 0
end

warn "Curation validation: FAIL (#{errors.length} issue#{'s' unless errors.length == 1})"
errors.each { |error| warn "  - #{error}" }
exit 1

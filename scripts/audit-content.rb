#!/usr/bin/env ruby
# scripts/audit-content.rb — Content taxonomy audit
# Reports: post count, topic counts, unknown categories, suspicious assignments,
# duplicate/case-variant tags, missing titles, empty display_title

require 'yaml'
require 'find'

POSTS_DIR = '_posts'
DATA_DIR = '_data'

# Load topics
topics_file = File.join(DATA_DIR, 'topics.yml')
topics_data = YAML.load_file(topics_file)
canonical_topics = topics_data['topics'].map { |t| t['name'] }

# Scan posts
posts = Dir.glob(File.join(POSTS_DIR, '*.md')).sort
post_count = posts.length

# Track stats
topic_counts = Hash.new(0)
unknown_categories = []
suspicious = []
tag_variants = Hash.new { |h, k| h[k] = [] }
missing_titles = []
empty_display_title = []

posts.each do |file|
  content = File.read(file)
  
  # Parse frontmatter
  if content =~ /\A---\s*\n(.*?)\n---\s*\n/m
    begin
      frontmatter = YAML.safe_load($1, permitted_classes: [Time]) || {}
    rescue => e
      frontmatter = {}
    end
  else
    frontmatter = {}
  end
  
  title = frontmatter['title'] || ''
  # Keep "absent" and "present but blank" apart. `display_title` is an optional
  # override used by 117 of 357 posts; conflating the two made this report 240
  # false positives the moment it was allowed to fail, which is how the bug had
  # been hiding behind an unconditional exit 0.
  has_display_title = frontmatter.key?('display_title')
  display_title = frontmatter['display_title']
  categories = frontmatter['categories'] || []
  tags = frontmatter['tags'] || []
  
  # Check topic (first category)
  topic = categories.first || 'Unknown'
  topic_counts[topic] += 1
  
  unless canonical_topics.include?(topic)
    unknown_categories << { file: file, topic: topic, title: title }
  end
  
  # Check for missing title
  missing_titles << file if title.to_s.strip.empty?
  empty_display_title << file if has_display_title && display_title.to_s.strip.empty?
  
  # Suspicious classifications
  title_lower = title.downcase
  
  if title_lower.include?('c++') && topic != 'C & C++'
    suspicious << { file: file, title: title, topic: topic, suggested: 'C & C++' }
  end
  
  if title_lower.include?('cmake') && !['C & C++', 'Developer Tools'].include?(topic)
    suspicious << { file: file, title: title, topic: topic, suggested: 'C & C++ / Developer Tools' }
  end
  
  if title_lower.include?('gdb') && !['Developer Tools', 'C & C++'].include?(topic)
    suspicious << { file: file, title: title, topic: topic, suggested: 'Developer Tools / C & C++' }
  end
  
  if title_lower.include?('linux') && topic == 'Personal'
    suspicious << { file: file, title: title, topic: topic, suggested: 'Systems / Computer Science' }
  end
  
  if title_lower.include?('ubuntu') && topic == 'Personal'
    suspicious << { file: file, title: title, topic: topic, suggested: 'Systems / Computer Science' }
  end
  
  if title_lower.include?('docker') && !['DevOps & Infrastructure', 'Systems'].include?(topic)
    suspicious << { file: file, title: title, topic: topic, suggested: 'DevOps & Infrastructure' }
  end
  
  if title_lower.include?('vllm') && topic != 'AI & LLM'
    suspicious << { file: file, title: title, topic: topic, suggested: 'AI & LLM' }
  end
  
  # Tag normalization
  tags.each do |tag|
    tag_variants[tag.to_s.downcase] << tag
  end
end

# Report
puts "=" * 60
puts "Content Taxonomy Audit Report"
puts "=" * 60
puts
puts "Posts: #{post_count}"
puts
puts "Topic Counts:"
canonical_topics.each do |topic|
  puts "  #{topic}: #{topic_counts[topic]}"
end
puts
puts "Unknown Categories: #{unknown_categories.length}"
unknown_categories.each do |item|
  puts "  #{item[:file]}"
  puts "    topic: #{item[:topic]}"
  puts "    title: #{item[:title]}"
end
puts
puts "Suspicious Classifications: #{suspicious.length}"
suspicious.each do |item|
  puts "  #{item[:file]}"
  puts "    title: #{item[:title]}"
  puts "    topic: #{item[:topic]}"
  puts "    suggested: #{item[:suggested]}"
end
puts
puts "Tag Variants (case/format):"
tag_variants.each do |key, variants|
  unique = variants.uniq
  if unique.length > 1
    puts "  #{unique.join(' / ')}"
  end
end
puts
puts "Missing Titles: #{missing_titles.length}"
missing_titles.each { |f| puts "  #{f}" }
puts
puts "Empty display_title (has title): #{empty_display_title.length}"
empty_display_title.each { |f| puts "  #{f}" }

# ---------------------------------------------------------------------------
# Exit status
#
# This script used to always exit 0, so all eleven acceptance gates could stay
# green while the taxonomy quietly drifted. Three different failure classes are
# now distinguished:
#
#   hard    -- a post with no title, a category that is not in topics.yml, or an
#              empty display_title next to a real title. These are defects.
#   ratchet -- "suspicious" classifications and tag case variants are heuristics,
#              not verdicts, so failing on today's 31 would block on judgement
#              calls. Instead the count is pinned to a baseline and the gate
#              fails only when it grows, which catches new drift without
#              forcing a cleanup of the existing set. Lower the baseline in this
#              file after reviewing and fixing items.
#   info    -- everything else.
# ---------------------------------------------------------------------------
BASELINE_SUSPICIOUS = 31
BASELINE_TAG_VARIANTS = 3

hard_failures = unknown_categories.length + missing_titles.length + empty_display_title.length
tag_variant_count = tag_variants.count { |_key, variants| variants.uniq.length > 1 }
problems = []
problems << "#{unknown_categories.length} post(s) in a category absent from topics.yml" if unknown_categories.any?
problems << "#{missing_titles.length} post(s) with no title" if missing_titles.any?
problems << "#{empty_display_title.length} post(s) with an empty display_title" if empty_display_title.any?

warns = []
if suspicious.length > BASELINE_SUSPICIOUS
  warns << "suspicious classifications grew from #{BASELINE_SUSPICIOUS} to #{suspicious.length}"
end
if tag_variant_count > BASELINE_TAG_VARIANTS
  warns << "tag case/format variants grew from #{BASELINE_TAG_VARIANTS} to #{tag_variant_count}"
end

puts
puts "=== Audit status ==="
puts "  hard failures:      #{hard_failures}"
puts "  suspicious:         #{suspicious.length} (baseline #{BASELINE_SUSPICIOUS})"
puts "  tag variant groups: #{tag_variant_count} (baseline #{BASELINE_TAG_VARIANTS})"
if hard_failures.zero? && warns.empty?
  puts "  Content taxonomy audit: PASS"
  exit 0
end
(hard_failures.zero? ? warns : problems + warns).each { |m| warn "  FAIL: #{m}" }
warn "Content taxonomy audit: FAIL"
exit 1

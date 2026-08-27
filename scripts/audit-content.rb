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
  display_title = frontmatter['display_title'] || ''
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
  empty_display_title << file if display_title.to_s.strip.empty? && !title.to_s.strip.empty?
  
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
    tag_variants[tag.downcase] << tag
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

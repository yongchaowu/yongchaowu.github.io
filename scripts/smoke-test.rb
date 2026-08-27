#!/usr/bin/env ruby
# scripts/smoke-test.rb
# Verify generated _site/ after jekyll build.
# Usage: ruby scripts/smoke-test.rb

require 'json'

SITE_DIR = File.join(__dir__, '..', '_site')
errors = []

def check(label, condition, detail = '')
  if condition
    puts "  ✓ #{label}"
  else
    puts "  ✗ #{label}#{detail ? ' — ' + detail : ''}"
    return false
  end
  true
end

puts "=== Smoke tests ==="
puts

# Basic structure
puts "Structure:"
check('_site/index.html exists', File.exist?(File.join(SITE_DIR, 'index.html')))
check('_site/search/index.html exists', File.exist?(File.join(SITE_DIR, 'search', 'index.html')))
check('_site/tag/index.html exists', File.exist?(File.join(SITE_DIR, 'tag', 'index.html')))
check('_site/category/index.html exists', File.exist?(File.join(SITE_DIR, 'category', 'index.html')))
check('_site/archive/index.html exists', File.exist?(File.join(SITE_DIR, 'archive', 'index.html')))
puts

# Search JSON
puts "Search JSON:"
search_path = File.join(SITE_DIR, 'search.json')
if File.exist?(search_path)
  begin
    data = JSON.parse(File.read(search_path))
    check("Valid JSON", true)
    check("Entry count matches posts (#{data.length})", data.length == 314)
    
    missing_url = data.find { |e| !e['url'] || e['url'].empty? }
    check("All entries have URL", missing_url.nil?)
    
    missing_title = data.find { |e| !e['title'] || e['title'].empty? }
    check("All entries have title", missing_title.nil?)
    
    missing_dt = data.find { |e| !e['display_title'] || e['display_title'].empty? }
    check("All entries have display_title", missing_dt.nil?)
    
    missing_topic = data.find { |e| !e['topic'] || e['topic'].empty? }
    check("All entries have topic", missing_topic.nil?)
    
    not_array = data.find { |e| !e['tags'].is_a?(Array) }
    check("tags is array for all entries", not_array.nil?)
  rescue JSON::ParserError => e
    check("Valid JSON", false, e.message)
  end
else
  check("search.json exists", false)
end
puts

# JS assets
puts "JS assets:"
check('js/search.js exists', File.exist?(File.join(SITE_DIR, 'js', 'search.js')))
check('js/toc.js exists', File.exist?(File.join(SITE_DIR, 'js', 'toc.js')))
check('js/tags.js exists', File.exist?(File.join(SITE_DIR, 'js', 'tags.js')))
check('js/pageContent.js exists', File.exist?(File.join(SITE_DIR, 'js', 'pageContent.js')))

# No Liquid in JS
%w[search.js toc.js tags.js pageContent.js].each do |js|
  content = File.read(File.join(SITE_DIR, 'js', js))
  has_liquid = content.include?('{{') || content.include?('{%')
  check("#{js} has no Liquid tags", !has_liquid)
end
puts

# Post count
puts "Content:"
post_dirs = Dir.glob(File.join(SITE_DIR, '20*', '*', '*', '*')).select { |d| File.exist?(File.join(d, 'index.html')) }
check("Post pages generated (#{post_dirs.length})", post_dirs.length > 300)
puts

puts "=== Done ==="

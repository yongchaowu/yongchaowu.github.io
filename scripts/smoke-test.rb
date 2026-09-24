#!/usr/bin/env ruby
# scripts/smoke-test.rb
# Verify generated _site/ after jekyll build.
# Usage: ruby scripts/smoke-test.rb

require 'json'
require 'cgi'

SITE_DIR = File.join(__dir__, '..', '_site')
$failures = 0

def check(label, condition, detail = '')
  if condition
    puts "  ✓ #{label}"
  else
    puts "  ✗ #{label}#{detail ? ' — ' + detail : ''}"
    $failures += 1
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
check('_site/tag/408/index.html exists', File.exist?(File.join(SITE_DIR, 'tag', '408', 'index.html')))
check('_site/tag/linux-unix-system-programming/index.html exists', File.exist?(File.join(SITE_DIR, 'tag', 'linux-unix-system-programming', 'index.html')))
check('_site/category/index.html exists', File.exist?(File.join(SITE_DIR, 'category', 'index.html')))
check('_site/archive/index.html exists', File.exist?(File.join(SITE_DIR, 'archive', 'index.html')))
check('_site/curated/index.html exists', File.exist?(File.join(SITE_DIR, 'curated', 'index.html')))
check('_site/start-here/index.html exists', File.exist?(File.join(SITE_DIR, 'start-here', 'index.html')))
check('_site/about/index.html exists', File.exist?(File.join(SITE_DIR, 'about', 'index.html')))
topic_pages = Dir.glob(File.join(SITE_DIR, 'topics', '*', 'index.html')).count
check("All topic pages generated (#{topic_pages})", topic_pages == 11)
leaked_paths = %w[scripts docs graphify-out vendor .github AGENTS.md README.md LICENSE Gemfile Gemfile.lock Todo].select { |name| File.exist?(File.join(SITE_DIR, name)) }
leaked_paths.concat(Dir.glob(File.join(SITE_DIR, '**', '*.map')))
check('Repository-only files and source maps excluded', leaked_paths.empty?, leaked_paths.first(5).join(', '))
html_files = Dir.glob(File.join(SITE_DIR, '**', '*.html'))
unresolved_markup = html_files.select do |path|
  content = File.read(path)
  content.include?('href="{%') || content.include?('{{ $') || content.include?('href=""')
end
check('Generated HTML has no unresolved Liquid/empty links', unresolved_markup.empty?, unresolved_markup.first(3).join(', '))
sitemap_path = File.join(SITE_DIR, 'sitemap.xml')
check('Search route excluded from sitemap', !File.exist?(sitemap_path) || !File.read(sitemap_path).include?('/search/'))
puts

# Search JSON
puts "Search JSON:"
search_path = File.join(SITE_DIR, 'search.json')
search_data = nil
if File.exist?(search_path)
  begin
    data = JSON.parse(File.read(search_path))
    search_data = data
    check("Valid JSON", true)
    source_post_count = Dir.glob(File.join(SITE_DIR, '..', '_posts', '*.md')).length
    check("Entry count matches posts (#{data.length})", data.length == source_post_count)
    
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
    curated_count = data.count { |e| e['curated'] == true }
    check("Curated entries present (#{curated_count})", curated_count > 0)
    known_editorial = data.find { |e| e['url'].to_s.include?('curated-cpp-backend-engineering') }
    check('Editorial sidecar reaches search index', known_editorial && known_editorial['content_type'] == 'roadmap' && known_editorial['placement'] == 'featured')
    tested_count = data.count { |e| e['verification'] == 'reported-tested' }
    check("Reported-tested editorial entries present (#{tested_count})", tested_count >= 5)
  rescue JSON::ParserError => e
    check("Valid JSON", false, e.message)
  end
else
  check("search.json exists", false)
end
puts

# Posts metadata JSON
puts "Posts metadata JSON:"
meta_path = File.join(SITE_DIR, 'posts-meta.json')
if File.exist?(meta_path)
  begin
    meta_data = JSON.parse(File.read(meta_path))
    check('Valid JSON', true)
    check("Entry count matches search index (#{meta_data.length})", meta_data.length == search_data&.length)
    check('All entries have URL', meta_data.all? { |entry| entry['url'] && !entry['url'].empty? })
    check('All entries have tags array', meta_data.all? { |entry| entry['tags'].is_a?(Array) })
  rescue JSON::ParserError => e
    check('Valid JSON', false, e.message)
  end
else
  check('posts-meta.json exists', false)
end
if search_data
  missing_routes = search_data.each_with_object([]) do |entry, missing|
    decoded_url = CGI.unescape(entry['url'].to_s.gsub('+', '%2B'))
    target = File.join(SITE_DIR, decoded_url.sub(%r{\A/}, ''), 'index.html')
    missing << entry['url'] unless File.file?(target)
  end
  check('All search-index routes exist', missing_routes.empty?, missing_routes.first(5).join(', '))
  urls = search_data.map { |entry| entry['url'] }
  check('Search-index URLs are unique', urls.length == urls.uniq.length)
end
puts

# JS assets
puts "JS assets:"
check('js/search.js exists', File.exist?(File.join(SITE_DIR, 'js', 'search.js')))
check('js/toc.js exists', File.exist?(File.join(SITE_DIR, 'js', 'toc.js')))
check('js/tags.js exists', File.exist?(File.join(SITE_DIR, 'js', 'tags.js')))
check('js/pageContent.js exists', File.exist?(File.join(SITE_DIR, 'js', 'pageContent.js')))
check('js/main.js exists', File.exist?(File.join(SITE_DIR, 'js', 'main.js')))
check('js/copy-code.js exists', File.exist?(File.join(SITE_DIR, 'js', 'copy-code.js')))

# No Liquid in JS
%w[search.js toc.js tags.js pageContent.js main.js copy-code.js].each do |js|
  content = File.read(File.join(SITE_DIR, 'js', js))
  has_liquid = content.include?('{{') || content.include?('{%')
  check("#{js} has no Liquid tags", !has_liquid)
end
search_page = File.read(File.join(SITE_DIR, 'search', 'index.html'))
search_script = File.read(File.join(SITE_DIR, 'js', 'search.js'))
tag_script = File.read(File.join(SITE_DIR, 'js', 'tags.js'))
check('Search exposes base URL to client', search_page.include?('data-base-url='))
check('Search result links use base URL', search_script.include?('baseUrl + hit.p.url'))
check('Tag result links use base URL', tag_script.include?('baseUrl + p.url'))
puts

# Post count
puts "Content:"
source_post_count = Dir.glob(File.join(SITE_DIR, '..', '_posts', '*.md')).length
post_dirs = Dir.glob(File.join(SITE_DIR, '20*', '*', '*', '*')).select { |d| File.exist?(File.join(d, 'index.html')) }
check("Post pages generated (#{post_dirs.length})", post_dirs.length == source_post_count)
pagination_pages = Dir.glob(File.join(SITE_DIR, 'page*', 'index.html')).count { |path| File.basename(File.dirname(path)).match?(/^page\d+$/) }
check("Home pagination generated (#{pagination_pages + 1} pages)", pagination_pages + 1 == (source_post_count / 10.0).ceil)
curated_urls = search_data.to_a.select { |entry| entry['curated'] == true }.map { |entry| entry['url'] }
curated_dirs = curated_urls.map { |url| decoded_url = CGI.unescape(url.to_s.gsub('+', '%2B')); File.join(SITE_DIR, decoded_url.sub(%r{\A/}, ''), 'index.html') }.select { |path| File.file?(path) }
check("Curated post pages generated (#{curated_dirs.length})", curated_dirs.length == curated_urls.length)
curated_html = curated_dirs.map { |path| File.read(path) }.join("\n")
check('Curated posts have no raw _posts links', !curated_html.include?('href="_posts/'))
check('Curated source notes resolve', !curated_html.include?('source-posts-missing'))
puts

puts "=== Done ==="
exit($failures.zero? ? 0 : 1)

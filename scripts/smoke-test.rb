#!/usr/bin/env ruby
# scripts/smoke-test.rb
# Verify generated _site/ after jekyll build.
# Usage: ruby scripts/smoke-test.rb

require 'json'
require 'cgi'
require 'date'
require 'rexml/document'
require 'yaml'

REPO_DIR = File.expand_path('..', __dir__)
SITE_DIR = ENV.fetch('SITE_DIR', File.join(REPO_DIR, '_site'))
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

unless Dir.exist?(SITE_DIR)
  warn "Generated site directory does not exist: #{SITE_DIR}"
  exit 2
end

puts "=== Smoke tests ==="
puts

# Basic structure
puts "Structure:"
required_routes = {
  'index.html' => 'home',
  '404.html' => '404',
  'search/index.html' => 'search',
  'tag/index.html' => 'tag index',
  'category/index.html' => 'category',
  'archive/index.html' => 'archive',
  'curated/index.html' => 'curated',
  'start-here/index.html' => 'start here',
  'about/index.html' => 'about'
}
required_routes.each do |relative_path, label|
  check("_site/#{relative_path} exists (#{label})", File.file?(File.join(SITE_DIR, relative_path)))
end
not_found_path = File.join(SITE_DIR, '404.html')
check('_site/404.html is noindex', File.file?(not_found_path) && File.read(not_found_path).include?('noindex'))

source_topic_count = Dir.glob(File.join(REPO_DIR, 'topics', '*.md')).count
topic_pages = Dir.glob(File.join(SITE_DIR, 'topics', '*', 'index.html')).count
check("All source topic pages generated (#{topic_pages}/#{source_topic_count})", topic_pages == source_topic_count)

source_tag_pages = Dir.glob(File.join(REPO_DIR, 'tag', '*', 'index.md'))
missing_tag_routes = source_tag_pages.filter_map do |source_path|
  permalink = File.read(source_path)[/^permalink:\s*(\S+)/, 1]
  target = permalink && File.join(SITE_DIR, permalink.sub(%r{\A/}, ''), 'index.html')
  source_path unless target && File.file?(target)
end
check("All source tag routes generated (#{source_tag_pages.length - missing_tag_routes.length}/#{source_tag_pages.length})", missing_tag_routes.empty?, missing_tag_routes.first(5).join(', '))

leaked_paths = %w[scripts docs graphify-out vendor .github AGENTS.md README.md LICENSE Gemfile Gemfile.lock Todo wyclswq.top-master-modification-plan.md].select { |name| File.exist?(File.join(SITE_DIR, name)) }
leaked_paths.concat(Dir.glob(File.join(SITE_DIR, '**', '*.map')))
check('Repository-only files and source maps excluded', leaked_paths.empty?, leaked_paths.first(5).join(', '))
html_files = Dir.glob(File.join(SITE_DIR, '**', '*.html'))
unresolved_markup = html_files.select do |path|
  content = File.read(path)
  content.include?('href="{%') || content.include?('{{ $') || content.include?('href=""')
end
check('Generated HTML has no unresolved Liquid/empty links', unresolved_markup.empty?, unresolved_markup.first(3).join(', '))

# Scripts that hide an element by setting `.hidden` rely on `[hidden] { display: none }`,
# but that rule lives in the UA stylesheet and loses to ANY author `display`
# declaration. `.tag-btn` is `display: inline-flex`, which silently turned the
# tag-page filter box into a no-op: tags.js set `link.hidden = true` and all 241 chips
# stayed visible. None of the other gates can see this — the HTML is valid, the JS is
# syntactically fine, and the built route exists — so assert the shipped CSS keeps the
# override that makes `.hidden` authoritative again.
css_path = File.join(SITE_DIR, 'css', 'main.css')
if File.file?(css_path)
  # Strip comments first: the SCSS explains this rule in prose, and the minifier
  # keeps that comment, so a naive match would "find" `[hidden] { display: none }`
  # inside the comment text and pass a build that never shipped the override.
  css = File.read(css_path).gsub(%r{/\*.*?\*/}m, ' ')
  hidden_rules = css.scan(/\[hidden\]\s*\{([^}]*)\}/m).flatten
  forces_none = hidden_rules.any? { |body| body.gsub(/\s+/, '').include?('display:none!important') }
  conflicting = hidden_rules.reject { |body| body.gsub(/\s+/, '').match?(/display:\s*none/) }
  check('Shipped CSS forces [hidden] to display:none', forces_none && conflicting.empty?,
        "rules=#{hidden_rules.length} important=#{forces_none} conflicting=#{conflicting.length}")
else
  check('Shipped CSS forces [hidden] to display:none', false, 'css/main.css missing')
end

sitemap_path = File.join(SITE_DIR, 'sitemap.xml')
if File.file?(sitemap_path)
  begin
    REXML::Document.new(File.read(sitemap_path))
    check('sitemap.xml is valid XML', true)
  rescue REXML::ParseException => e
    check('sitemap.xml is valid XML', false, e.message)
  end
  check('Search route excluded from sitemap', !File.read(sitemap_path).include?('/search/'))
else
  check('sitemap.xml exists', false)
end
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
    source_post_count = Dir.glob(File.join(REPO_DIR, '_posts', '*.md')).length
    check("Entry count matches posts (#{data.length})", data.length == source_post_count)
    
    missing_url = data.find { |e| !e['url'] || e['url'].empty? }
    check("All entries have URL", missing_url.nil?)
    
    missing_title = data.find { |e| !e['title'] || e['title'].empty? }
    check("All entries have title", missing_title.nil?)
    
    missing_dt = data.find { |e| !e['display_title'] || e['display_title'].empty? }
    check("All entries have display_title", missing_dt.nil?)

    # The body corpus moved to search-text.json so the first paint only needs the
    # small metadata index (~44 KB gzipped instead of ~842 KB). These two checks
    # are about the article text, so they must read that file — reading them off
    # search.json would make the entity check pass vacuously (no text at all) and
    # break the punctuation check outright.
    text_path = File.join(SITE_DIR, 'search-text.json')
    text_index = File.exist?(text_path) ? (JSON.parse(File.read(text_path)) rescue nil) : nil
    check('search-text.json exists', !text_index.nil?)
    if text_index
      check('Text corpus covers the same posts', text_index.size == data.length)
      index_urls = data.map { |e| e['url'] }.sort
      check('Text corpus URLs match the index', index_urls == text_index.keys.sort)
      check('Metadata index carries no body text', data.none? { |e| e.key?('text') })
      entity_index = text_index.find { |_url, body| body.to_s.match?(/&(?:lt|gt|amp|quot|#39);/i) }
      check('Search index decodes common HTML entities', entity_index.nil?, entity_index && entity_index[0])
      cpp_url = data.map { |e| e['url'] }.find { |u| u.to_s.include?('C++-Performance-Analysis') }
      check('Exact code punctuation is searchable',
            cpp_url && text_index[cpp_url].to_s.include?('std::vector<int>'),
            cpp_url && "no text for #{cpp_url}")
    end
    
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
    attribution_count = data.count { |e| e['attribution'].is_a?(Hash) }
    check("Attribution records reach search index (#{attribution_count})", attribution_count >= 3)
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
    meta_attribution_count = meta_data.count { |entry| entry['attribution'].is_a?(Hash) }
    check("Attribution records reach posts metadata (#{meta_attribution_count})", meta_attribution_count >= 3)
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
base_match = search_page.match(/data-base-url="([^"]*)"/)
check('Search exposes a data-base-url attribute', !base_match.nil?)
base_url = base_match && base_match[1]
expected_base_url = ENV['PAGES_BASE_PATH'].to_s
check('data-base-url is normalized', base_url.nil? || base_url.empty? || (base_url.start_with?('/') && base_url.end_with?('/')))
normalized_base_url = base_url.to_s.chomp('/')
normalized_expected_base_url = expected_base_url.chomp('/')
if normalized_expected_base_url.empty?
  check('data-base-url matches the Pages build path', base_url.to_s.empty?)
else
  check('data-base-url matches the Pages build path', normalized_base_url == normalized_expected_base_url)
end
check('Search result links use base URL', search_script.include?('baseUrl + hit.p.url'))
check('Tag result links use base URL', tag_script.include?('baseUrl + p.url'))
puts

# Post count
puts "Content:"
source_post_count = Dir.glob(File.join(REPO_DIR, '_posts', '*.md')).length
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

# Crawl root-relative links in generated HTML. This catches broken internal
# routes while deliberately ignoring external, fragment-only and non-HTML URLs.
missing_internal_links = []
html_files.each do |html_path|
  content = File.read(html_path)
  content.scan(/(?:href|action)=["']([^"']+)["']/i).flatten.each do |href|
    next if href.empty? || href.start_with?('#', '//', 'http://', 'https://', 'mailto:', 'tel:', 'javascript:', 'data:')
    next unless href.start_with?('/')

    route = CGI.unescape(href.split(/[?#]/, 2).first.to_s.gsub('+', '%2B'))
    if base_url && !base_url.empty?
      next unless route == base_url.chomp('/') || route.start_with?(base_url)
      relative_route = route.delete_prefix(base_url)
    else
      relative_route = route.sub(%r{\A/}, '')
    end
    relative_route = relative_route.sub(%r{\A/+}, '')
    candidates = if relative_route.empty? || route.end_with?('/')
                   [File.join(SITE_DIR, relative_route, 'index.html')]
                 else
                   [File.join(SITE_DIR, relative_route), File.join(SITE_DIR, relative_route, 'index.html')]
                 end
    next if candidates.any? { |candidate| File.file?(candidate) }
    missing_internal_links << "#{html_path.sub(SITE_DIR, '')} -> #{href}"
  end
end
check("Generated internal links resolve (#{missing_internal_links.length} missing)", missing_internal_links.empty?, missing_internal_links.first(5).join(' | '))
puts


# ---------------------------------------------------------------------------
# Regressions added 2026-10-01 after docs/review-2026-10-01.md.
#
# Every check above verifies the repository's internal self-consistency. None of
# them looked at the relationship between the document and what it claims, which
# is how an RSS feed shipped 7 of 10 items with empty descriptions, 267 Chinese
# articles declared lang="en", and every post page declared structured data twice
# while the whole pipeline stayed green. These close those gaps.
# ---------------------------------------------------------------------------
puts
puts "=== Content and metadata claims (added 2026-10-01) ==="

post_meta_path = File.join(REPO_DIR, '_data', 'post_meta.yml')
if check('_data/post_meta.yml exists', File.file?(post_meta_path))
  post_meta = YAML.safe_load(File.read(post_meta_path), permitted_classes: [Date, Time]) || {}
  sidecar = post_meta['posts'] || {}

  # --- Feed descriptions must not be empty ---------------------------------
  feed_path = File.join(SITE_DIR, 'feed.xml')
  if check('feed.xml exists', File.file?(feed_path))
    feed = File.read(feed_path)
    items = feed.scan(%r{<item>(.*?)</item>}m).flatten
    check("Feed carries items (#{items.length})", items.length.positive?)
    blank = items.select do |item|
      desc = item[%r{<description>(.*?)</description>}m, 1].to_s.strip
      desc.length < 5
    end
    check('Every feed item has a non-empty description', blank.empty?,
          "#{blank.length} blank of #{items.length}")
    %w[<language> <managingEditor>].each do |element|
      check("Feed declares #{element}", feed.include?(element))
    end
    check('Feed has no raw unescaped ampersands in titles',
          feed.scan(%r{<title>[^<]*&(?!amp;|lt;|gt;|quot;|apos;|#)[^<]*</title>}).empty?)
  end

  # --- Language metadata must be self-consistent ---------------------------
  # Catches the original bug directly: 267 Chinese articles inherited
  # site.lang: en and emitted lang="en" / og:locale="en" / "inLanguage": "en".
  sample = html_files.select { |f| f.include?('/20') && f.end_with?('index.html') }
  lang_mismatch = []
  sample.each do |path|
    content = File.read(path)
    html_lang = content[%r{<html[^>]*\blang="([^"]*)"}m, 1]
    og_locale = content[%r{<meta property="og:locale" content="([^"]*)"}m, 1]
    in_language = content[/"inLanguage":\s*"([^"]*)"/m, 1]
    next if html_lang.nil?
    mismatches = []
    mismatches << "html=#{html_lang}" if og_locale && og_locale != html_lang.tr('-', '_')
    mismatches << "jsonld=#{in_language}" if in_language && in_language != html_lang
    lang_mismatch << "#{path.sub(SITE_DIR, '')}: #{mismatches.join(' ')}" unless mismatches.empty?
  end
  check("Document language metadata agrees across html/og/json-ld (#{lang_mismatch.length} bad)",
        lang_mismatch.empty?, lang_mismatch.first(3).join(' | '))

  # The sidecar must actually cover every post, and a post that declares its own
  # language must not be contradicted by the sidecar.
  contradicted = sidecar.select do |path, meta|
    fm_path = File.join(REPO_DIR, path)
    next false unless File.file?(fm_path)
    declared = File.read(fm_path)[/^lang:\s*(\S+)/, 1]
    declared && declared != meta['lang']
  end
  check("Sidecar agrees with declared front-matter lang (#{contradicted.length} bad)",
        contradicted.empty?, contradicted.keys.first(3).join(', '))
  check("Sidecar covers all posts (#{sidecar.length})", sidecar.length == source_post_count)
end

# --- The permalink is a real contract, and it is timezone-derived ---------------
# `permalink: /:year/:month/:day/:title/` is derived from each post's front-matter
# date, and Jekyll interprets a naive `date:` value in the *build machine's* zone.
# 78 of the 357 posts carry a time between 00:00 and 08:00 local, so before
# `timezone: UTC` was declared in _config.yml a build running in Asia/Shanghai moved
# those 78 URLs back one day. CI set TZ=UTC, so the live site served the correct
# ones while local previews silently disagreed -- which made AGENTS.md's "the
# permalink is part of the public URL contract" untrue across environments.
#
# The check is a join on the filename contract rather than on post metadata: the
# filenames are already `YYYY-MM-DD-slug.md` and AGENTS.md requires the filename
# date to equal the front-matter date, so the generated directory must be exactly
# that pair. No timezone interpretation happens in the test itself.
declared_tz = begin
  cfg = YAML.safe_load(File.read(File.join(REPO_DIR, '_config.yml')), permitted_classes: [Date, Time])
  cfg.is_a?(Hash) ? cfg['timezone'] : nil
rescue StandardError
  nil
end
check("_config.yml declares an explicit timezone (got #{declared_tz.inspect})",
      declared_tz.to_s != '')

# A direct filename->slug join is not possible: Jekyll does not use the filename
# verbatim. `开篇·序` publishes as `开篇-序`, `3DES（Triple-DES）` as
# `3DES-Triple-DES`, so an assertion built on that assumption fails on 34 posts
# for the wrong reason.
#
# Instead compare multisets. The front-matter date is read as raw text, so the test
# itself performs no timezone conversion; the published date comes from the
# sitemap. If a build shifts even one article across a day boundary the two
# multisets stop matching, which is exactly the regression this guards.
require 'set'
fm_dates = Hash.new(0)
Dir.glob(File.join(REPO_DIR, '_posts', '*.md')).sort.each do |file|
  head = File.read(file)[/\A---\s*\n(.*?)\n---\s*\n/m, 1]
  next unless head
  raw = head[/^date:\s*["']?(\d{4})-(\d{2})-(\d{2})/, 1]
  next unless raw
  fm_dates["#{Regexp.last_match(1)}/#{Regexp.last_match(2)}/#{Regexp.last_match(3)}"] += 1
end

url_dates = Hash.new(0)
sitemap = File.join(SITE_DIR, 'sitemap.xml')
if File.file?(sitemap)
  File.read(sitemap).scan(%r{<loc>https?://[^/]+/(\d{4})/(\d{2})/(\d{2})/}).each do |y, mo, d|
    url_dates["#{y}/#{mo}/#{d}"] += 1
  end
end
check("Sitemap article dates match front-matter dates exactly (#{url_dates.values.sum} URLs)",
      fm_dates == url_dates,
      "front matter has #{fm_dates.size} distinct dates, sitemap has #{url_dates.size}; "       "first difference: #{(fm_dates.keys | url_dates.keys).sort.find { |k| fm_dates[k] != url_dates[k] }.inspect}")

# --- Cards must not render an empty description -------------------------------
# 7 posts ship no front-matter summary and have an empty excerpt, because their
# <!--more--> marker sits on the first body line. The feed was fixed first and the
# cards were left blank, which is the same defect in a different place.
empty_cards = []
html_files.each do |path|
  content = File.read(path)
  content.scan(%r{<p>\s*</p>}).each { empty_cards << path.sub(SITE_DIR, '') }
  content.scan(%r{<div class="excerpt">\s*</div>}).each { empty_cards << path.sub(SITE_DIR, '') }
end
check("No rendered card has an empty description (#{empty_cards.length})",
      empty_cards.empty?, empty_cards.first(3).join(', '))

if File.file?(post_meta_path)
  # --- Inferred language must not be an outright inversion --------------------
  # The first classifier used a flat 20-CJK-character threshold, which called a
  # 7-character all-Chinese post `en` and a 50/50 post `zh-CN`. A mislabel is
  # only acceptable when it is visible, so low-confidence records are counted and
  # inversions are refused outright.
  inversions = sidecar.select do |_path, meta|
    cjk = meta['cjk_chars'].to_i
    words = meta['latin_words'].to_i
    next false unless meta['lang_source'] == 'inferred'
    (meta['lang'] == 'en' && cjk > words && cjk >= 20) ||
      (meta['lang'] == 'zh-CN' && words > cjk * 3 && words >= 60)
  end
  check("Inferred language is never an outright inversion (#{inversions.length})",
        inversions.empty?, inversions.keys.first(3).join(', '))

  low = sidecar.count { |_p, m| m['lang_confidence'] == 'low' }
  puts "  · #{low} posts carry a low-confidence inferred language (too little prose to call)"

  # A post has no card text only when it has no prose at all. The sidecar is the
  # authority on that -- it already strips headings, lists, links, HTML and code,
  # which a second implementation in Ruby would only approximate (the first
  # attempt here counted 4 prose-free posts against 12 blanks and failed).
  blank_cards = sidecar.select { |_p, m| m['card_summary'].to_s.strip.empty? }
  prose_free = sidecar.select { |_p, m| m['cjk_chars'].to_i.zero? && m['latin_words'].to_i.zero? }
  unexplained = blank_cards.keys - prose_free.keys
  check("Only genuinely prose-free posts lack card text (#{blank_cards.length} blank, #{prose_free.length} prose-free)",
        unexplained.empty?, unexplained.first(3).join(', '))
end

# --- Structured data must be declared exactly once --------------------------
# _layouts/post.html used to add an itemscope/itemtype with no itemprop inside,
# duplicating the JSON-LD graph that _includes/seo-jsonld.html already emits.
microdata = html_files.select { |f| File.read(f).include?('itemtype=') }
check("No duplicate microdata structured data (#{microdata.length} pages)",
      microdata.empty?, microdata.first(3).map { |f| f.sub(SITE_DIR, '') }.join(', '))

multi_ld = html_files.select do |f|
  File.read(f).scan('application/ld+json').length > 1
end
check("No page carries more than one JSON-LD block (#{multi_ld.length} pages)",
      multi_ld.empty?, multi_ld.first(3).map { |f| f.sub(SITE_DIR, '') }.join(', '))

# --- Static assets must be cache-busted -------------------------------------
# Favicons already carried ?v=; CSS and JavaScript carried nothing, so a
# returning visitor could pair new HTML with a stale stylesheet.
unversioned = []
html_files.each do |path|
  File.read(path).scan(%r{(?:src|href)="(/(?:css|js)/[^"?]*)(\?[^"]*)?"}i).each do |asset, query|
    unversioned << "#{path.sub(SITE_DIR, '')} -> #{asset}" if query.nil? || query == '?v='
  end
end
check("Every CSS/JS reference is cache-versioned (#{unversioned.length} unversioned)",
      unversioned.empty?, unversioned.first(5).join(' | '))

# --- Mixed content ----------------------------------------------------------
# Browsers block active http:// images on an https:// origin, so they silently
# disappear rather than failing loudly.
mixed = []
html_files.each do |path|
  File.read(path).scan(%r{<img[^>]*\ssrc="(http://[^"]+)"}i).flatten.each do |src|
    mixed << "#{path.sub(SITE_DIR, '')} -> #{src}"
  end
end
check("No http:// images (mixed content, silently blocked) (#{mixed.length})",
      mixed.empty?, mixed.first(5).join(' | '))

puts "=== Done ==="
exit($failures.zero? ? 0 : 1)

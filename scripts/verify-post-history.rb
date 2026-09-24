#!/usr/bin/env ruby
# frozen_string_literal: true

# Verify that posts present in the pre-curation baseline still exist with the
# same Git blob. New posts are allowed; historical edits require an explicit
# baseline update and URL/reference review.
#
# Usage: ruby scripts/verify-post-history.rb
# Override the baseline only for an intentional migration:
#   POST_HISTORY_BASELINE=<commit> ruby scripts/verify-post-history.rb

require 'open3'
require 'set'
require 'yaml'
require 'date'

BASELINE = ENV.fetch('POST_HISTORY_BASELINE', 'b1dc48b52cc291e1ca771bd514ed2cf251b14054')
FORMAT_FIXES_FILE = File.expand_path('../_data/format_fixes.yml', __dir__)
failures = []

def git_lines(repo, *args)
  stdout, stderr, status = Open3.capture3('git', '-C', repo, '-c', 'core.quotePath=false', *args)
  raise "git #{args.join(' ')} failed: #{stderr.strip}" unless status.success?

  stdout.lines.map(&:chomp)
end

repo = File.expand_path('..', __dir__)
unless system('git', '-C', repo, 'cat-file', '-e', "#{BASELINE}^{commit}", out: File::NULL, err: File::NULL)
  warn "Post-history check: baseline commit not found: #{BASELINE}"
  exit 1
end

baseline_posts = Set.new(git_lines(repo, 'ls-tree', '-r', '--name-only', BASELINE, '--', '_posts').select { |path| path.end_with?('.md') })
current_posts = Set.new(git_lines(repo, 'ls-tree', '-r', '--name-only', 'HEAD', '--', '_posts').select { |path| path.end_with?('.md') })
failures << "expected 331 baseline posts, found #{baseline_posts.length}" unless baseline_posts.length == 331
format_fixes = (YAML.safe_load_file(FORMAT_FIXES_FILE, permitted_classes: [Date], aliases: false) || {}).fetch('fixes', [])
format_fix_paths = Hash.new(0)
format_fix_blobs = {}
format_fixes.each do |fix|
  path = fix['post'].to_s
  format_fix_paths[path] += 1
  failures << "format fix does not target a baseline post: #{path}" unless baseline_posts.include?(path)
  failures << "format fix is missing a reason: #{path}" if fix['reason'].to_s.strip.empty?

  fixed_blob = fix['fixed_blob'].to_s
  if fixed_blob.empty?
    failures << "format fix is missing fixed_blob: #{path}"
  elsif fixed_blob !~ /\A[0-9a-f]{40}\z/
    failures << "format fix fixed_blob is not a Git blob ID: #{path}"
  end
  format_fix_blobs[path] = fixed_blob
end
format_fix_paths.each do |path, count|
  failures << "format fix path is duplicated: #{path}" if count > 1
end

baseline_posts.each do |path|
  baseline_blob, = Open3.capture3('git', '-C', repo, 'rev-parse', "#{BASELINE}:#{path}")

  if format_fix_paths.key?(path)
    actual_blob, = Open3.capture3('git', '-C', repo, 'hash-object', '--', path)
    expected_blob = format_fix_blobs[path]
    unless actual_blob.strip == expected_blob
      failures << "format fix blob mismatch: #{path} (expected #{expected_blob}, got #{actual_blob.strip})"
    end
    next
  end

  current_blob, = Open3.capture3('git', '-C', repo, 'rev-parse', "HEAD:#{path}")
  if current_blob.strip.empty?
    failures << "deleted historical post: #{path}"
  elsif current_blob.strip != baseline_blob.strip
    failures << "modified historical post: #{path}"
  end
end

# New posts may still be edited locally before commit; historical baseline
# posts may not have uncommitted changes.
changed_posts = (git_lines(repo, 'diff', '--name-only', '--', '_posts') +
                git_lines(repo, 'diff', '--cached', '--name-only', '--', '_posts')).uniq
changed_posts.each do |path|
  failures << "uncommitted historical post change: #{path}" if baseline_posts.include?(path) && !format_fix_paths.key?(path)
end

puts "Baseline: #{BASELINE}"
puts "Historical posts checked: #{baseline_posts.size}"
puts "New posts allowed: #{(current_posts - baseline_posts).size}"
puts "Explicit approved exceptions: #{format_fix_paths.size}"
if failures.empty?
  puts 'Post history verification: PASS'
  exit 0
end

warn "Post history verification: FAIL (#{failures.length} issue#{'s' unless failures.length == 1})"
failures.each { |failure| warn "  - #{failure}" }
exit 1

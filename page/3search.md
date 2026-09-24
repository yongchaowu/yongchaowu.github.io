---
layout: default
title: Search
display_title: 'Search / 搜索'
description: "Search titles, tags, topics and full article text across the Yc.W archive."
permalink: /search/
icon: search
type: page
noindex: true
sitemap: false
---

{% assign normalized_baseurl = site.baseurl %}
{% if normalized_baseurl == '/' %}{% assign normalized_baseurl = '' %}{% elsif normalized_baseurl and normalized_baseurl != '' %}{% assign normalized_baseurl = normalized_baseurl | append: '/' %}{% endif %}
<main class="page search-page" id="main-content" tabindex="-1">
    <noscript>
        <div class="noscript-note"><strong>Search needs JavaScript.</strong> You can still browse <a href="{{ '/tag/' | relative_url }}">tags</a>, <a href="{{ '/category/' | relative_url }}">topics</a>, or the <a href="{{ '/archive/' | relative_url }}">complete archive</a>.</div>
    </noscript>
    <header class="search-header">
        <div>
            <span class="section-kicker">Find a thread</span>
            <h1>Search the notebook</h1>
            <p>搜索标题、标签、主题和文章正文；也可以只查看精选重组文章。</p>
        </div>
        <a class="button button--quiet" href="{{ '/start-here/' | relative_url }}">Not sure where to start?</a>
    </header>

    <div class="search-wrap" id="search-app" data-index-url="{{ '/search.json' | relative_url }}" data-base-url="{{ normalized_baseurl }}">
        <div class="search-input-wrap">
            {% include icon.html name="search" %}
            <label class="sr-only" for="search-input">Search the notebook</label>
            <input id="search-input" type="search" inputmode="search" enterkeyhint="search" placeholder="Try “CMake”, “LLM”, or “dynamic linker”" autocomplete="off" spellcheck="false">
        </div>
        <div id="topic-filter" class="topic-filter" aria-label="Filter search results">
            <button type="button" class="topic-filter-btn active" data-topic="" aria-pressed="true">All notes</button>
            <button type="button" class="topic-filter-btn curated-filter-btn" data-curated="true" aria-pressed="false">Curated only</button>
            {% for topic in site.data.topics.topics %}
            <button type="button" class="topic-filter-btn" data-topic="{{ topic.name | escape }}" aria-pressed="false">{{ topic.name }}</button>
            {% endfor %}
        </div>
        <div class="search-select-filters">
            <label for="type-filter">Content type
                <select id="type-filter">
                    <option value="">All types</option>
                    <option value="roadmap">Roadmap</option>
                    <option value="deep-dive">Deep dive</option>
                    <option value="note">Note</option>
                    <option value="runbook">Runbook</option>
                    <option value="tutorial">Tutorial</option>
                    <option value="reference">Reference</option>
                    <option value="case-study">Case study</option>
                    <option value="lab-guide">Lab guide</option>
                    <option value="editorial">Editorial</option>
                </select>
            </label>
            <label for="status-filter">Evidence
                <select id="status-filter">
                    <option value="">Any status</option>
                    <option value="reported-tested">Reported tested source</option>
                    <option value="editorial-review">Editorial review</option>
                    <option value="not-tested">Not tested</option>
                    <option value="review-required">Review required</option>
                    <option value="unknown">Unknown / not classified</option>
                </select>
            </label>
        </div>
        <p id="search-stats" aria-live="polite"></p>
        <ul id="search-results"></ul>
    </div>

    <div class="search-tips">
        <strong>Search tips</strong>
        <span>Use a topic filter for a narrower shelf. Use <em>Curated only</em> when you want source-linked guides instead of raw notes.</span>
    </div>
</main>
<script src="{{ '/js/search.js' | relative_url }}" charset="utf-8"></script>

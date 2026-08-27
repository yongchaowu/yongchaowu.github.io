---
layout: page
title: Search
permalink: /search/
icon: search
type: page
---

<div class="search-wrap" id="search-app" data-index-url="{{ '/search.json' | relative_url }}">
    <input id="search-input" type="text" placeholder="Search titles, tags, content…" autocomplete="off" autofocus>
    <div id="topic-filter" class="topic-filter">
        <button class="topic-filter-btn active" data-topic="">All</button>
        {% for topic in site.data.topics.topics %}
        <button class="topic-filter-btn" data-topic="{{ topic.name | escape }}">{{ topic.name }}</button>
        {% endfor %}
    </div>
    <p id="search-stats"></p>
    <ul id="search-results"></ul>
</div>

<style>
.topic-filter {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin: 10px 0;
}
.topic-filter-btn {
    padding: 3px 10px;
    border: 1px solid var(--border-color, #ccc);
    border-radius: 4px;
    background: none;
    color: var(--text-secondary);
    font-size: 12px;
    cursor: pointer;
    transition: 0.2s;
}
.topic-filter-btn:hover {
    border-color: var(--text-primary);
    color: var(--text-primary);
}
.topic-filter-btn.active {
    background: var(--badge-text);
    color: var(--bg-content);
    border-color: var(--badge-text);
}
.search-topic {
    font-size: 11px;
    padding: 1px 6px;
    background: var(--badge-bg);
    color: var(--badge-text);
    border-radius: 3px;
    margin-right: 4px;
}
</style>

<script src="{{ '/js/search.js' | relative_url }}" charset="utf-8"></script>

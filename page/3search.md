---
layout: page
title: Search
permalink: /search/
icon: search
type: page
---

<div class="search-wrap">
    <input id="search-input" type="text" placeholder="Search titles, tags, content…" autocomplete="off" autofocus>
    <p id="search-stats"></p>
    <ul id="search-results"></ul>
</div>

<script src="{{ "/js/search.js " | prepend: site.baseurl }}" charset="utf-8"></script>

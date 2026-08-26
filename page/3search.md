---
layout: page
title: 搜索
permalink: /search/
icon: search
type: page
---

<div class="search-wrap">
    <input id="search-input" type="text" placeholder="搜索标题、标签、正文…" autocomplete="off" autofocus>
    <p id="search-stats"></p>
    <ul id="search-results"></ul>
</div>

<script src="{{ "/js/search.js " | prepend: site.baseurl }}" charset="utf-8"></script>

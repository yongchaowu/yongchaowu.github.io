/* jshint asi:true */
/**
 * search.js — client-side search over search.json
 */
(function() {
    var input = document.getElementById('search-input')
    var results = document.getElementById('search-results')
    var stats = document.getElementById('search-stats')
    if (!input || !results) return

    var DATA = null
    var LOADING = false

    function load(cb) {
        if (DATA) return cb()
        if (LOADING) return setTimeout(function() { load(cb) }, 200)
        LOADING = true
        stats.textContent = 'Loading index…'
        var xhr = new XMLHttpRequest()
        xhr.open('GET', '{{ "/search.json" | prepend: site.baseurl }}', true)
        xhr.onload = function() {
            try {
                DATA = JSON.parse(xhr.responseText)
                stats.textContent = ''
            } catch (e) {
                stats.textContent = 'Index failed to load'
            }
            LOADING = false
            cb()
        }
        xhr.onerror = function() { stats.textContent = 'Index failed to load'; LOADING = false }
        xhr.send()
    }

    function esc(s) {
        return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    }

    function snippet(text, q) {
        var i = text.toLowerCase().indexOf(q)
        if (i < 0) return esc(text.slice(0, 80)) + '…'
        var start = Math.max(0, i - 40)
        var frag = text.slice(start, start + 140)
        return esc(frag).replace(new RegExp(esc(q).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'), function(m) {
            return '<mark>' + m + '</mark>'
        })
    }

    function render(q) {
        var terms = q.toLowerCase().split(/\s+/).filter(Boolean)
        if (!terms.length) {
            results.innerHTML = ''
            stats.textContent = ''
            return
        }
        var hits = []
        for (var i = 0; i < DATA.length && hits.length < 30; i++) {
            var p = DATA[i]
            var hay = (p.title + ' ' + p.tags.join(' ') + ' ' + p.categories.join(' ') + ' ' + p.text).toLowerCase()
            var titleHay = p.title.toLowerCase()
            var tagHay = (p.tags.join(' ') + ' ' + p.categories.join(' ')).toLowerCase()
            var ok = true
            for (var j = 0; j < terms.length; j++) {
                if (hay.indexOf(terms[j]) < 0) { ok = false; break }
            }
            if (!ok) continue
            var score = 0
            for (var k = 0; k < terms.length; k++) {
                if (titleHay.indexOf(terms[k]) >= 0) score += 10
                if (tagHay.indexOf(terms[k]) >= 0) score += 5
                score += 1
            }
            hits.push({ p: p, score: score })
        }
        hits.sort(function(a, b) { return b.score - a.score })
        stats.textContent = hits.length ? hits.length + ' results' : 'No matching posts found'
        results.innerHTML = hits.slice(0, 30).map(function(h) {
            var t = esc(h.p.title).replace(new RegExp(terms.map(function(x){return x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}).join('|'), 'gi'), function(m) {
                return '<mark>' + m + '</mark>'
            })
            return '<li class="search-hit"><time>' + h.p.date + '</time>' +
                '<a href="' + h.p.url + '">' + t + '</a>' +
                '<p>' + snippet(h.p.text, terms[0]) + '</p></li>'
        }).join('')
    }

    var timer = null
    input.addEventListener('input', function() {
        clearTimeout(timer)
        timer = setTimeout(function() {
            load(function() { render(input.value.trim()) })
        }, 250)
    })

    // auto-fill from ?q=
    var m = location.search.match(/[?&]q=([^&]*)/)
    if (m) {
        input.value = decodeURIComponent(m[1])
        load(function() { render(input.value.trim()) })
    }
}())

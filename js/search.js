/* jshint asi:true */
/**
 * search.js — client-side search over search.json
 */
(function() {
    var input = document.getElementById('search-input')
    var results = document.getElementById('search-results')
    var stats = document.getElementById('search-stats')
    var app = document.getElementById('search-app')
    var filterEl = document.getElementById('topic-filter')
    if (!input || !results || !app) return

    var indexUrl = app.getAttribute('data-index-url')
    var DATA = null
    var LOADING = false
    var selectedTopic = ''

    function load(cb) {
        if (DATA) return cb()
        if (LOADING) return setTimeout(function() { load(cb) }, 200)
        LOADING = true
        stats.textContent = 'Loading index…'
        var xhr = new XMLHttpRequest()
        xhr.open('GET', indexUrl, true)
        xhr.onload = function() {
            if (xhr.status < 200 || xhr.status >= 300) {
                stats.textContent = 'Index failed to load (HTTP ' + xhr.status + ')'
                LOADING = false
                return
            }
            try {
                DATA = JSON.parse(xhr.responseText)
                stats.textContent = ''
                buildTopicFilter()
            } catch (e) {
                stats.textContent = 'Index failed to parse'
            }
            LOADING = false
            cb()
        }
        xhr.onerror = function() { stats.textContent = 'Index failed to load'; LOADING = false }
        xhr.send()
    }

    function buildTopicFilter() {
        if (!filterEl || !DATA) return

        // Topic buttons are server-rendered; just attach click handlers
        var btns = filterEl.querySelectorAll('.topic-filter-btn')
        for (var k = 0; k < btns.length; k++) {
            btns[k].onclick = function() {
                selectedTopic = this.getAttribute('data-topic')
                var all = filterEl.querySelectorAll('.topic-filter-btn')
                for (var x = 0; x < all.length; x++) all[x].classList.remove('active')
                this.classList.add('active')
                updateUrl()
                doSearch()
            }
        }

        // Apply topic from URL
        var tm = location.search.match(/[?&]topic=([^&]*)/)
        if (tm) {
            selectedTopic = decodeURIComponent(tm[1].replace(/\+/g, ' '))
            var allBtns = filterEl.querySelectorAll('.topic-filter-btn')
            for (var b = 0; b < allBtns.length; b++) {
                if (allBtns[b].getAttribute('data-topic') === selectedTopic) {
                    allBtns[b].classList.add('active')
                } else {
                    allBtns[b].classList.remove('active')
                }
            }
        }
    }

    function updateUrl() {
        var params = []
        var q = input.value.trim()
        if (q) params.push('q=' + encodeURIComponent(q))
        if (selectedTopic) params.push('topic=' + encodeURIComponent(selectedTopic))
        var url = location.pathname + (params.length ? '?' + params.join('&') : '')
        history.replaceState(null, '', url)
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

    function doSearch() {
        render(input.value.trim())
    }

    function render(q) {
        var terms = q.toLowerCase().split(/\s+/).filter(Boolean)
        if (!terms.length && !selectedTopic) {
            results.innerHTML = ''
            stats.textContent = ''
            return
        }
        var hits = []
        for (var i = 0; i < DATA.length; i++) {
            var p = DATA[i]

            // Topic filter
            if (selectedTopic && p.topic !== selectedTopic) continue

            // If no search terms, show all in topic
            if (!terms.length) {
                hits.push({ p: p, score: 1, date: p.date || '' })
                continue
            }

            var displayTitle = p.display_title || p.title || ''
            var hay = [
                displayTitle,
                p.title || '',
                p.topic || '',
                (p.tags || []).join(' '),
                (p.categories || []).join(' '),
                p.text || ''
            ].join(' ').toLowerCase()

            var ok = true
            for (var j = 0; j < terms.length; j++) {
                if (hay.indexOf(terms[j]) < 0) { ok = false; break }
            }
            if (!ok) continue

            var score = 0
            var titleLower = displayTitle.toLowerCase()
            var topicLower = (p.topic || '').toLowerCase()
            var tagHay = (p.tags || []).join(' ').toLowerCase()
            var catHay = (p.categories || []).join(' ').toLowerCase()

            for (var k = 0; k < terms.length; k++) {
                var t = terms[k]
                if (titleLower === t) score += 50
                else if (titleLower.indexOf(t) >= 0) score += 20
                if (topicLower.indexOf(t) >= 0) score += 12
                if (tagHay.indexOf(t) >= 0) score += 8
                if (catHay.indexOf(t) >= 0) score += 5
                if (hay.indexOf(t) >= 0) score += 1
            }
            hits.push({ p: p, score: score, date: p.date || '' })
        }
        hits.sort(function(a, b) {
            if (b.score !== a.score) return b.score - a.score
            return (b.date > a.date) ? 1 : (b.date < a.date) ? -1 : 0
        })
        stats.textContent = hits.length ? hits.length + ' results' : 'No matching posts found'
        results.innerHTML = hits.slice(0, 30).map(function(h) {
            var titleText = h.p.display_title || h.p.title
            var t = esc(titleText).replace(new RegExp(terms.map(function(x){return x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}).join('|'), 'gi'), function(m) {
                return '<mark>' + m + '</mark>'
            })
            var topic = h.p.topic ? '<span class="search-topic">' + esc(h.p.topic) + '</span> ' : ''
            return '<li class="search-hit"><time>' + h.p.date + '</time> ' + topic +
                '<a href="' + h.p.url + '">' + t + '</a>' +
                '<p>' + (terms.length ? snippet(h.p.text, terms[0]) : '') + '</p></li>'
        }).join('')
    }

    var timer = null
    input.addEventListener('input', function() {
        clearTimeout(timer)
        timer = setTimeout(function() {
            updateUrl()
            load(function() { render(input.value.trim()) })
        }, 250)
    })

    // auto-fill from ?q= and ?topic=
    var m = location.search.match(/[?&]q=([^&]*)/)
    if (m) {
        input.value = decodeURIComponent(m[1].replace(/\+/g, ' '))
    }
    load(function() { render(input.value.trim()) })
}())

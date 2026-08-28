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
                LOADING = false
                return
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

    var PAGE_SIZE = 30
    var allHits = []
    var shownCount = 0

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

    function renderHit(hit, terms) {
        var li = document.createElement('li')
        li.className = 'search-hit'
        var time = document.createElement('time')
        time.textContent = hit.p.date
        li.appendChild(time)
        li.appendChild(document.createTextNode(' '))
        if (hit.p.topic) {
            var span = document.createElement('span')
            span.className = 'search-topic'
            span.textContent = hit.p.topic
            li.appendChild(span)
            li.appendChild(document.createTextNode(' '))
        }
        var a = document.createElement('a')
        a.href = hit.p.url
        var titleText = hit.p.display_title || hit.p.title
        if (terms.length) {
            a.innerHTML = esc(titleText).replace(new RegExp(terms.map(function(x){return x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}).join('|'), 'gi'), function(m) {
                return '<mark>' + m + '</mark>'
            })
        } else {
            a.textContent = titleText
        }
        li.appendChild(a)
        if (terms.length) {
            var p = document.createElement('p')
            p.innerHTML = snippet(hit.p.text, terms[0])
            li.appendChild(p)
        }
        return li
    }

    function renderShowMore() {
        var existing = document.getElementById('search-show-more')
        if (existing) existing.remove()
        if (shownCount < allHits.length) {
            var btn = document.createElement('button')
            btn.id = 'search-show-more'
            btn.className = 'search-show-more'
            btn.textContent = 'Show more (' + shownCount + ' / ' + allHits.length + ')'
            btn.onclick = function() {
                var terms = input.value.trim().toLowerCase().split(/\s+/).filter(Boolean)
                var end = Math.min(shownCount + PAGE_SIZE, allHits.length)
                for (var i = shownCount; i < end; i++) {
                    results.appendChild(renderHit(allHits[i], terms))
                }
                shownCount = end
                if (shownCount < allHits.length) {
                    stats.textContent = allHits.length + ' results \u00b7 showing ' + shownCount
                } else {
                    stats.textContent = allHits.length + ' results'
                }

                renderShowMore()
            }
            results.parentElement.appendChild(btn)
        }
    }

    function doSearch() {
        render(input.value.trim())
    }

    function render(q) {
        var terms = q.toLowerCase().split(/\s+/).filter(Boolean)
        if (!terms.length && !selectedTopic) {
            results.innerHTML = ''
            stats.textContent = ''
            allHits = []
            shownCount = 0
            var oldMore = document.getElementById('search-show-more')
            if (oldMore) oldMore.remove()
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
        allHits = hits
        shownCount = 0
        var existingMore = document.getElementById('search-show-more')
        if (existingMore) existingMore.remove()
        if (!hits.length) {
            stats.textContent = 'No matching posts found'
            results.innerHTML = ''
            return
        }
        var visible = Math.min(PAGE_SIZE, hits.length)
        var suffix = hits.length > PAGE_SIZE ? ' · showing ' + visible : ''
        stats.textContent = hits.length + ' results' + suffix
        results.innerHTML = ''
        for (var n = 0; n < visible; n++) {
            results.appendChild(renderHit(hits[n], terms))
        }
        shownCount = visible
        renderShowMore()
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

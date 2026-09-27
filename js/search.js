/* jshint asi:true */
/**
 * search.js — client-side search over a two-part index.
 *
 * Phase 1  search.json      ~44 KB gzipped: titles, tags, topics, summaries and
 *                            the editorial fields. Searchable as soon as it
 *                            arrives, so the first keystroke never waits on the
 *                            article corpus.
 * Phase 2  search-text.json ~822 KB gzipped: the stripped body of every post,
 *                            fetched once the page is idle. Merging it only ever
 *                            ADDS matches, so full-text coverage is preserved
 *                            rather than traded away for speed; results simply
 *                            improve a moment after first paint.
 *
 * Before the split the single index was 2.5 MB / 842 KB gzipped (92% of it body
 * text) and a 400 kbps connection needed 57s before the first result appeared.
 */
(function() {
    var input = document.getElementById('search-input')
    var results = document.getElementById('search-results')
    var stats = document.getElementById('search-stats')
    var app = document.getElementById('search-app')
    var filterEl = document.getElementById('topic-filter')
    var typeFilter = document.getElementById('type-filter')
    var statusFilter = document.getElementById('status-filter')
    if (!input || !results || !app) return

    var indexUrl = app.getAttribute('data-index-url')
    var textUrl = app.getAttribute('data-text-url')
    var DATA = null
    var LOADING = false
    var LOAD_ERROR = false
    var callbacks = []
    var selectedTopic = ''
    var selectedType = ''
    var selectedStatus = ''
    var curatedOnly = false
    var baseUrl = app.getAttribute('data-base-url') || ''
    var PAGE_SIZE = 30
    var allHits = []
    var shownCount = 0
    var timer = null
    // Phase 2 state: 'idle' | 'loading' | 'ready' | 'error'
    var TEXT_STATE = textUrl ? 'idle' : 'ready'
    var TEXT_SCHEDULED = false
    var CACHE_PREFIX = 'ycw-search-text:'

    function load(cb) {
        if (DATA) return cb()
        if (LOADING) {
            callbacks.push(cb)
            return
        }
        callbacks.push(cb)
        LOADING = true
        LOAD_ERROR = false
        app.setAttribute('aria-busy', 'true')
        if (stats) stats.textContent = 'Loading index…'
        var xhr = new XMLHttpRequest()
        xhr.open('GET', indexUrl, true)
        xhr.onload = function() {
            if (xhr.status < 200 || xhr.status >= 300) {
                finishLoad(null, 'Index failed to load (HTTP ' + xhr.status + ')')
                return
            }
            try {
                DATA = JSON.parse(xhr.responseText)
                prepareData()
                finishLoad(null, '')
            } catch (e) {
                finishLoad(null, 'Index failed to parse')
            }
        }
        xhr.onerror = function() { finishLoad(null, 'Index failed to load') }
        xhr.send()
    }

    function finishLoad(error, message) {
        LOADING = false
        app.removeAttribute('aria-busy')
        if (error) {
            LOAD_ERROR = true
            if (stats) stats.textContent = message
        } else if (stats && message) {
            stats.textContent = message
        }
        var pending = callbacks.slice()
        callbacks = []
        for (var i = 0; i < pending.length; i++) pending[i](error)
        if (!error) scheduleText()
    }

    function decodeEntities(value) {
        return String(value || '')
            .replace(/&lt;/gi, '<')
            .replace(/&gt;/gi, '>')
            .replace(/&quot;/gi, '"')
            .replace(/&#0*39;|&apos;|&#x0*27;/gi, "'")
            .replace(/&amp;/gi, '&')
    }

    function prepareData() {
        for (var i = 0; i < DATA.length; i++) {
            var p = DATA[i]
            p._snippet = decodeEntities(p.summary || '')
            p._titleLower = decodeEntities(p.display_title || p.title || '').toLowerCase()
            p._topicLower = decodeEntities(p.topic || '').toLowerCase()
            p._tagLower = decodeEntities((p.tags || []).join(' ')).toLowerCase()
            p._categoryLower = decodeEntities((p.categories || []).join(' ')).toLowerCase()
            p._metaHaystack = [
                p.display_title || '',
                p.title || '',
                p.topic || '',
                (p.tags || []).join(' '),
                (p.categories || []).join(' '),
                p._snippet
            ].join(' ').toLowerCase()
            p._haystack = p._metaHaystack
        }
    }

    // Phase 2: fold the body corpus into the haystacks. Purely additive — a post
    // keeps every match it had in phase 1 and gains body matches.
    function applyTextMap(map) {
        if (!map) return
        for (var i = 0; i < DATA.length; i++) {
            var p = DATA[i]
            var body = map[p.url]
            if (!body) continue
            p._snippet = decodeEntities(body)
            p._haystack = p._metaHaystack + ' ' + p._snippet.toLowerCase()
        }
    }

    function textCacheKey() {
        var newest = ''
        for (var i = 0; i < DATA.length; i++) {
            if (!newest || DATA[i].date > newest) newest = DATA[i].date
        }
        return CACHE_PREFIX + DATA.length + ':' + newest
    }

    function readTextCache(key) {
        try {
            var raw = sessionStorage.getItem(key)
            return raw ? JSON.parse(raw) : null
        } catch (e) { return null }
    }

    function writeTextCache(key, map) {
        try { sessionStorage.setItem(key, JSON.stringify(map)) } catch (e) {}
    }

    function loadText() {
        if (TEXT_STATE === 'ready' || TEXT_STATE === 'loading' || !textUrl) return
        TEXT_STATE = 'loading'
        var key = textCacheKey()
        var cached = readTextCache(key)
        if (cached) {
            applyTextMap(cached)
            TEXT_STATE = 'ready'
            if (hasIntent()) render(input.value.trim())
            return
        }
        var xhr = new XMLHttpRequest()
        xhr.open('GET', textUrl, true)
        xhr.onload = function() {
            if (xhr.status < 200 || xhr.status >= 300) { TEXT_STATE = 'error'; return }
            var map = null
            try { map = JSON.parse(xhr.responseText) } catch (e) { TEXT_STATE = 'error'; return }
            applyTextMap(map)
            writeTextCache(key, map)
            TEXT_STATE = 'ready'
            if (hasIntent()) render(input.value.trim())
        }
        xhr.onerror = function() { TEXT_STATE = 'error' }
        xhr.send()
    }

    // Kick phase 2 off only when the browser is idle, so it never competes with
    // the first render or the user's first keystrokes.
    function scheduleText() {
        if (TEXT_SCHEDULED || TEXT_STATE === 'ready' || !textUrl) return
        TEXT_SCHEDULED = true
        var run = function() { loadText() }
        if (typeof window.requestIdleCallback === 'function') {
            window.requestIdleCallback(run, { timeout: 3000 })
        } else {
            window.setTimeout(run, 1200)
        }
    }

    function esc(s) {
        return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    }

    function currentTerms() {
        return decodeEntities(input.value.trim()).toLowerCase().split(/\s+/).filter(Boolean)
    }

    function hasIntent() {
        return Boolean(input.value.trim() || selectedTopic || selectedType || selectedStatus || curatedOnly)
    }

    function requestRender() {
        if (hasIntent()) {
            load(function(error) {
                if (!error) render(input.value.trim())
            })
        } else {
            render('')
        }
    }

    function updateUrl() {
        var params = []
        var q = input.value.trim()
        if (q) params.push('q=' + encodeURIComponent(q))
        if (selectedTopic) params.push('topic=' + encodeURIComponent(selectedTopic))
        if (selectedType) params.push('type=' + encodeURIComponent(selectedType))
        if (selectedStatus) params.push('status=' + encodeURIComponent(selectedStatus))
        if (curatedOnly) params.push('curated=1')
        var url = location.pathname + (params.length ? '?' + params.join('&') : '')
        try { history.replaceState(null, '', url) } catch (e) {}
    }

    function readUrlState() {
        var params
        try {
            params = new URLSearchParams(location.search)
        } catch (e) {
            params = null
        }
        function get(name) {
            if (params) return params.get(name) || ''
            var match = location.search.match(new RegExp('[?&]' + name + '=([^&]*)'))
            return match ? decodeURIComponent(match[1].replace(/\+/g, ' ')) : ''
        }
        selectedTopic = get('topic')
        selectedType = get('type')
        selectedStatus = get('status')
        curatedOnly = get('curated') === '1'
        input.value = get('q')
    }

    function syncControls() {
        if (typeFilter) typeFilter.value = selectedType
        if (statusFilter) statusFilter.value = selectedStatus
        if (!filterEl) return
        var btns = filterEl.querySelectorAll('.topic-filter-btn')
        for (var i = 0; i < btns.length; i++) {
            var btn = btns[i]
            var isCurated = btn.getAttribute('data-curated') === 'true'
            var topic = btn.getAttribute('data-topic') || ''
            var isAll = !isCurated && !topic
            var active = isCurated ? curatedOnly : (!curatedOnly && (isAll ? !selectedTopic : topic === selectedTopic))
            btn.classList.toggle('active', active)
            btn.setAttribute('aria-pressed', active ? 'true' : 'false')
        }
    }

    function bindControls() {
        if (filterEl) {
            var btns = filterEl.querySelectorAll('.topic-filter-btn')
            for (var i = 0; i < btns.length; i++) {
                btns[i].addEventListener('click', function() {
                    var isCurated = this.getAttribute('data-curated') === 'true'
                    curatedOnly = isCurated
                    selectedTopic = isCurated ? '' : (this.getAttribute('data-topic') || '')
                    syncControls()
                    updateUrl()
                    requestRender()
                })
            }
        }
        if (typeFilter) {
            typeFilter.addEventListener('change', function() {
                selectedType = this.value
                updateUrl()
                requestRender()
            })
        }
        if (statusFilter) {
            statusFilter.addEventListener('change', function() {
                selectedStatus = this.value
                updateUrl()
                requestRender()
            })
        }
        input.addEventListener('input', function() {
            clearTimeout(timer)
            timer = setTimeout(function() {
                updateUrl()
                requestRender()
            }, 250)
        })
        window.addEventListener('popstate', function() {
            readUrlState()
            syncControls()
            requestRender()
        })
    }

    // Pick the window that shows the most query terms. The old version only ever
    // looked at terms[0], so a multi-word query could show an excerpt with none of
    // the other words in it.
    function snippet(text, terms) {
        var source = decodeEntities(text)
        if (!source) return ''
        var lower = source.toLowerCase()
        var list = terms && terms.length ? terms : ['']
        var best = -1
        var bestScore = -1
        for (var i = 0; i < list.length; i++) {
            var at = list[i] ? lower.indexOf(list[i]) : 0
            if (at < 0) continue
            var score = 0
            for (var j = 0; j < list.length; j++) {
                if (list[j] && lower.indexOf(list[j]) >= 0) score++
            }
            if (score > bestScore || (score === bestScore && at < best)) {
                bestScore = score
                best = at
            }
        }
        var start
        var frag
        if (best < 0) {
            frag = source.slice(0, 140)
        } else {
            start = Math.max(0, best - 40)
            frag = source.slice(start, start + 140)
        }
        var out = esc(frag)
        for (var k = 0; k < list.length; k++) {
            var q = list[k]
            if (!q) continue
            var safeQ = esc(q).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
            out = out.replace(new RegExp(safeQ, 'gi'), function(m) {
                return '<mark>' + m + '</mark>'
            })
        }
        return (start > 0 ? '…' : '') + out + (source.length > start + 140 ? '…' : '')
    }

    function renderHit(hit, terms) {
        var li = document.createElement('li')
        li.className = 'search-hit'
        var time = document.createElement('time')
        time.textContent = hit.p.date
        li.appendChild(time)
        var content = document.createElement('div')
        content.className = 'search-hit-content'
        if (hit.p.topic) {
            var span = document.createElement('span')
            span.className = 'search-topic'
            span.textContent = hit.p.topic
            content.appendChild(span)
            content.appendChild(document.createTextNode(' '))
        }
        if (hit.p.curated) {
            var curated = document.createElement('span')
            curated.className = 'search-topic search-topic--curated'
            curated.textContent = 'Curated'
            content.appendChild(curated)
            content.appendChild(document.createTextNode(' '))
        }
        if (hit.p.content_type) {
            var kind = document.createElement('span')
            kind.className = 'search-topic search-topic--type'
            kind.textContent = hit.p.content_type.replace(/-/g, ' ')
            content.appendChild(kind)
            content.appendChild(document.createTextNode(' '))
        }
        if (hit.p.verification && hit.p.verification !== 'unknown') {
            var status = document.createElement('span')
            status.className = 'search-topic search-topic--status'
            status.textContent = hit.p.verification.replace(/-/g, ' ')
            content.appendChild(status)
            content.appendChild(document.createTextNode(' '))
        }
        if (hit.p.origin && hit.p.origin !== 'author') {
            var origin = document.createElement('span')
            origin.className = 'search-topic search-topic--origin'
            origin.textContent = hit.p.origin.replace(/-/g, ' ')
            content.appendChild(origin)
            content.appendChild(document.createTextNode(' '))
        }
        var a = document.createElement('a')
        a.href = baseUrl + hit.p.url
        var titleText = hit.p.display_title || hit.p.title || 'Untitled note'
        if (terms.length) {
            a.innerHTML = esc(titleText).replace(new RegExp(terms.map(function(x) {
                return x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
            }).join('|'), 'gi'), function(m) {
                return '<mark>' + m + '</mark>'
            })
        } else {
            a.textContent = titleText
        }
        content.appendChild(a)
        if (terms.length) {
            var p = document.createElement('p')
            p.innerHTML = snippet(hit.p._snippet, terms)
            content.appendChild(p)
        }
        li.appendChild(content)
        return li
    }

    function renderShowMore() {
        var existing = document.getElementById('search-show-more')
        if (existing) existing.remove()
        if (shownCount < allHits.length) {
            var btn = document.createElement('button')
            btn.id = 'search-show-more'
            btn.className = 'search-show-more'
            btn.type = 'button'
            btn.textContent = 'Show more (' + shownCount + ' / ' + allHits.length + ')'
            btn.addEventListener('click', function() {
                var terms = currentTerms()
                var end = Math.min(shownCount + PAGE_SIZE, allHits.length)
                for (var i = shownCount; i < end; i++) results.appendChild(renderHit(allHits[i], terms))
                shownCount = end
                if (stats) stats.textContent = allHits.length + ' results · showing ' + shownCount
                renderShowMore()
            })
            results.parentElement.appendChild(btn)
        }
    }

    function renderDiscovery() {
        var existing = document.getElementById('search-discovery')
        if (existing) existing.remove()
        var div = document.createElement('div')
        div.id = 'search-discovery'
        div.className = 'search-discovery'
        div.innerHTML = '<h3>Popular Tags</h3>' +
            '<div class="search-discovery-tags">' +
            '<a href="' + baseUrl + '/tag/cpp/">C++</a>' +
            '<a href="' + baseUrl + '/tag/llm/">LLM</a>' +
            '<a href="' + baseUrl + '/tag/docker/">Docker</a>' +
            '<a href="' + baseUrl + '/tag/nvidia/">NVIDIA</a>' +
            '<a href="' + baseUrl + '/tag/ray/">Ray</a>' +
            '<a href="' + baseUrl + '/tag/python/">Python</a>' +
            '<a href="' + baseUrl + '/tag/linux/">Linux</a>' +
            '<a href="' + baseUrl + '/tag/cmake/">CMake</a>' +
            '</div>'
        results.parentElement.insertBefore(div, results)
    }

    function render(q) {
        var terms = decodeEntities(q).toLowerCase().split(/\s+/).filter(Boolean)
        if (!terms.length && !selectedTopic && !selectedType && !selectedStatus && !curatedOnly) {
            results.innerHTML = ''
            if (stats) stats.textContent = ''
            allHits = []
            shownCount = 0
            var oldMore = document.getElementById('search-show-more')
            if (oldMore) oldMore.remove()
            renderDiscovery()
            return
        }
        if (LOAD_ERROR || !DATA) {
            if (stats) stats.textContent = 'Search is temporarily unavailable.'
            return
        }
        var discovery = document.getElementById('search-discovery')
        if (discovery) discovery.remove()
        var hits = []
        for (var i = 0; i < DATA.length; i++) {
            var p = DATA[i]
            if (selectedTopic && p.topic !== selectedTopic) continue
            if (selectedType && p.content_type !== selectedType) continue
            if (selectedStatus && p.verification !== selectedStatus) continue
            if (curatedOnly && !p.curated) continue

            if (!terms.length) {
                hits.push({ p: p, score: 1, date: p.date || '' })
                continue
            }

            var ok = true
            for (var j = 0; j < terms.length; j++) {
                if (p._haystack.indexOf(terms[j]) < 0) {
                    ok = false
                    break
                }
            }
            if (!ok) continue

            var score = 0
            for (var k = 0; k < terms.length; k++) {
                var t = terms[k]
                if (p._titleLower === t) score += 50
                else if (p._titleLower.indexOf(t) >= 0) score += 20
                if (p._topicLower.indexOf(t) >= 0) score += 12
                if (p._tagLower.indexOf(t) >= 0) score += 8
                if (p._categoryLower.indexOf(t) >= 0) score += 5
                if (p._haystack.indexOf(t) >= 0) score += 1
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
            var hint = document.createElement('div')
            hint.className = 'search-empty'
            // While the body corpus is still in flight "no matches" is not a final
            // answer — say so instead of showing a confident dead end.
            var stillLoading = terms.length && TEXT_STATE === 'loading'
            hint.innerHTML = stillLoading
                ? '<p>No matches in titles, tags or summaries yet.</p>' +
                  '<p>The full-text index is still loading; results refresh when it arrives.</p>'
                : '<p>No matching posts found.</p>' +
                  '<p>Try fewer keywords, a broader topic, or browse tags.</p>' +
                  '<div class="search-suggestion-tags">' +
                  '<a href="' + baseUrl + '/tag/cpp/">C++</a>' +
                  '<a href="' + baseUrl + '/tag/linux/">Linux</a>' +
                  '<a href="' + baseUrl + '/tag/docker/">Docker</a>' +
                  '<a href="' + baseUrl + '/tag/llm/">LLM</a>' +
                  '<a href="' + baseUrl + '/tag/nvidia/">NVIDIA</a>' +
                  '</div>'
            results.innerHTML = ''
            results.appendChild(hint)
            if (stats) stats.textContent = ''
            return
        }
        var visible = Math.min(PAGE_SIZE, hits.length)
        var suffix = hits.length > PAGE_SIZE ? ' · showing ' + visible : ''
        if (stats) {
            stats.textContent = hits.length + ' results' + suffix
            // Be explicit that the body corpus is still arriving, otherwise a
            // user who searched early sees fewer hits and assumes that is all
            // there is. Only shown when it can still change the result set.
            if (terms.length && TEXT_STATE === 'loading') {
                var note = document.createElement('span')
                note.className = 'search-text-pending'
                note.textContent = ' · loading full-text index…'
                stats.appendChild(note)
            }
        }
        results.innerHTML = ''
        for (var n = 0; n < visible; n++) results.appendChild(renderHit(hits[n], terms))
        shownCount = visible
        renderShowMore()
    }

    readUrlState()
    bindControls()
    syncControls()
    if (hasIntent()) requestRender()
    else render('')
}())

/* jshint asi:true */
/**
 * search.js — client-side search over search.json
 *
 * The full index is intentionally lazy: the empty search page can render its
 * discovery links without downloading the multi-megabyte article index.
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
            p._plainText = decodeEntities(p.text)
            p._titleLower = decodeEntities(p.display_title || p.title || '').toLowerCase()
            p._haystack = [
                p.display_title || '',
                p.title || '',
                p.topic || '',
                (p.tags || []).join(' '),
                (p.categories || []).join(' '),
                p._plainText
            ].join(' ').toLowerCase()
            p._topicLower = decodeEntities(p.topic || '').toLowerCase()
            p._tagLower = decodeEntities((p.tags || []).join(' ')).toLowerCase()
            p._categoryLower = decodeEntities((p.categories || []).join(' ')).toLowerCase()
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

    function snippet(text, q) {
        var source = decodeEntities(text)
        var lower = source.toLowerCase()
        var i = lower.indexOf(q)
        if (i < 0) return esc(source.slice(0, 80)) + '…'
        var start = Math.max(0, i - 40)
        var frag = source.slice(start, start + 140)
        var safeQ = esc(q).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
        return esc(frag).replace(new RegExp(safeQ, 'gi'), function(m) {
            return '<mark>' + m + '</mark>'
        })
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
            p.innerHTML = snippet(hit.p.text, terms[0])
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
            hint.innerHTML = '<p>No matching posts found.</p>' +
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
        if (stats) stats.textContent = hits.length + ' results' + suffix
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

/* jshint asi:true */
/**
 * tags.js — tag index filtering/sorting and the legacy ?tag= view.
 */
(function() {
    var app = document.querySelector('[data-tag-index]')
    var postsEl = document.getElementById('tag-posts')
    var headingEl = document.getElementById('tag-heading')
    var listEl = document.getElementById('tag-post-list')
    if (!postsEl || !app) return

    var DATA = null
    var LOADING = false
    var indexUrl = app.getAttribute('data-index-url') || 'posts-meta.json'
    var baseUrl = app.getAttribute('data-base-url') || ''
    var filterInput = document.getElementById('tag-filter-input')
    var sortSelect = document.getElementById('tag-sort')
    var allTags = document.getElementById('all-tags')
    var emptyState = null

    function load(cb) {
        if (DATA) return cb()
        if (LOADING) return setTimeout(function() { load(cb) }, 200)
        LOADING = true
        var xhr = new XMLHttpRequest()
        xhr.open('GET', indexUrl, true)
        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                try { DATA = JSON.parse(xhr.responseText) } catch (e) {}
            }
            LOADING = false
            cb()
        }
        xhr.onerror = function() { LOADING = false; cb() }
        xhr.send()
    }

    function renderPostList(posts) {
        listEl.innerHTML = ''
        posts.forEach(function(p) {
            var li = document.createElement('li')
            var time = document.createElement('time')
            time.textContent = p.date
            li.appendChild(time)
            li.appendChild(document.createTextNode(' '))
            var a = document.createElement('a')
            a.href = baseUrl + p.url
            a.textContent = p.display_title || p.title
            li.appendChild(a)
            listEl.appendChild(li)
        })
    }

    function selectTag(tag) {
        if (!DATA) return
        var posts = DATA.filter(function(p) {
            return (p.tags || []).indexOf(tag) >= 0
        })
        posts.sort(function(a, b) { return (b.date > a.date) ? 1 : (b.date < a.date) ? -1 : 0 })

        headingEl.textContent = 'Tag: ' + tag + ' (' + posts.length + ' posts)'
        postsEl.style.display = 'block'
        if (!posts.length) {
            listEl.innerHTML = '<li class="tag-result-empty">No articles found for this tag. Browse the <a href="' + baseUrl + '/tag/">complete tag index</a>.</li>'
        } else {
            renderPostList(posts)
        }

        var url = location.pathname + '?tag=' + encodeURIComponent(tag)
        try { history.replaceState(null, '', url) } catch (e) {}

        var btns = document.querySelectorAll('.tag-btn')
        for (var i = 0; i < btns.length; i++) {
            btns[i].classList.toggle('active', btns[i].getAttribute('data-tag') === tag)
        }
    }

    function applyTagControls() {
        if (!allTags) return
        var query = filterInput ? filterInput.value.trim().toLowerCase() : ''
        var sort = sortSelect ? sortSelect.value : 'count'
        var links = Array.prototype.slice.call(allTags.querySelectorAll('.tag-btn'))
        links.sort(function(a, b) {
            if (sort === 'name') {
                return (a.getAttribute('data-tag-name') || a.textContent).localeCompare(b.getAttribute('data-tag-name') || b.textContent)
            }
            var ac = parseInt((a.querySelector('.tag-count') || {}).textContent || 0, 10)
            var bc = parseInt((b.querySelector('.tag-count') || {}).textContent || 0, 10)
            return bc - ac
        })
        var visible = 0
        links.forEach(function(link) {
            var name = (link.getAttribute('data-tag-name') || link.textContent).toLowerCase()
            var show = !query || name.indexOf(query) >= 0
            link.hidden = !show
            if (show) {
                allTags.appendChild(link)
                visible++
            }
        })
        if (emptyState) emptyState.remove()
        if (!visible) {
            emptyState = document.createElement('p')
            emptyState.className = 'tag-filter-empty'
            emptyState.textContent = 'No tags match this filter.'
            allTags.parentElement.appendChild(emptyState)
        }
    }

    if (filterInput) filterInput.addEventListener('input', applyTagControls)
    if (sortSelect) sortSelect.addEventListener('change', applyTagControls)
    applyTagControls()

    // Tag buttons remain ordinary canonical links; the optional ?tag= view is
    // retained only for legacy/bookmarked index URLs.
    var m = location.search.match(/[?&]tag=([^&]*)/)
    if (m) {
        var tag = decodeURIComponent(m[1].replace(/\+/g, ' '))
        load(function() { selectTag(tag) })
    }
}())

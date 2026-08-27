/* jshint asi:true */
/**
 * tags.js — dynamic tag index using search.json
 */
(function() {
    var featuredEl = document.getElementById('featured-tags')
    var allEl = document.getElementById('all-tags')
    var postsEl = document.getElementById('tag-posts')
    var headingEl = document.getElementById('tag-heading')
    var listEl = document.getElementById('tag-post-list')
    var sideEl = document.getElementById('content-side')
    if (!featuredEl || !allEl) return

    var DATA = null
    var LOADING = false
    var indexUrl = featuredEl.getAttribute('data-index-url') || '/search.json'

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

    function buildTagMap(posts) {
        var map = {}
        for (var i = 0; i < posts.length; i++) {
            var tags = posts[i].tags || []
            for (var j = 0; j < tags.length; j++) {
                var t = tags[j]
                if (!map[t]) map[t] = []
                map[t].push(posts[i])
            }
        }
        return map
    }

    function renderTagButtons(container, tags, tagCounts, activeTag) {
        container.innerHTML = ''
        for (var i = 0; i < tags.length; i++) {
            var btn = document.createElement('a')
            btn.className = 'tag-btn' + (tags[i] === activeTag ? ' active' : '')
            btn.setAttribute('data-tag', tags[i])
            btn.innerHTML = tags[i] + ' <span class="tag-count">(' + tagCounts[tags[i]] + ')</span>'
            btn.onclick = (function(tag) {
                return function(e) {
                    e.preventDefault()
                    selectTag(tag)
                }
            })(tags[i])
            container.appendChild(btn)
        }
    }

    function renderPostList(posts) {
        listEl.innerHTML = posts.map(function(p) {
            var title = p.display_title || p.title
            return '<li><time>' + p.date + '</time> ' +
                '<a href="' + p.url + '">' + title.replace(/</g, '&lt;') + '</a></li>'
        }).join('')
    }

    function selectTag(tag) {
        if (!DATA) return
        var tagMap = buildTagMap(DATA)
        var posts = tagMap[tag] || []
        posts.sort(function(a, b) { return (b.date > a.date) ? 1 : (b.date < a.date) ? -1 : 0 })

        headingEl.textContent = 'Tag: ' + tag + ' (' + posts.length + ' posts)'
        postsEl.style.display = 'block'
        renderPostList(posts)

        // update URL
        var url = location.pathname + '?tag=' + encodeURIComponent(tag)
        history.replaceState(null, '', url)

        // highlight active button
        var btns = document.querySelectorAll('.tag-btn')
        for (var i = 0; i < btns.length; i++) {
            btns[i].classList.toggle('active', btns[i].getAttribute('data-tag') === tag)
        }
    }

    load(function() {
        if (!DATA) {
            featuredEl.innerHTML = '<p>Failed to load tag index</p>'
            return
        }

        var tagMap = buildTagMap(DATA)
        var tagNames = Object.keys(tagMap).sort()
        var tagCounts = {}
        for (var i = 0; i < tagNames.length; i++) {
            tagCounts[tagNames[i]] = tagMap[tagNames[i]].length
        }

        // featured tags from data attribute (from _data/featured_tags.yml)
        var featuredStr = featuredEl.getAttribute('data-featured')
        var featured = []
        try { featured = JSON.parse(featuredStr) } catch (e) {}
        var featuredAvailable = featured.filter(function(t) { return tagCounts[t] })
        renderTagButtons(featuredEl, featuredAvailable, tagCounts, '')

        // all tags
        renderTagButtons(allEl, tagNames, tagCounts, '')

        // sidebar
        sideEl.innerHTML = tagNames.map(function(t) {
            return '<li><a data-scroll href="#tag-' + t.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase() + '">' + t + ' (' + tagCounts[t] + ')</a></li>'
        }).join('')

        // check ?tag= parameter
        var m = location.search.match(/[?&]tag=([^&]*)/)
        if (m) {
            var tag = decodeURIComponent(m[1].replace(/\+/g, ' '))
            if (tagCounts[tag]) selectTag(tag)
        }
    })
}())

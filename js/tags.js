/* jshint asi:true */
/**
 * tags.js — tag post listing (tags are server-rendered)
 */
(function() {
    var postsEl = document.getElementById('tag-posts')
    var headingEl = document.getElementById('tag-heading')
    var listEl = document.getElementById('tag-post-list')
    if (!postsEl) return

    var DATA = null
    var LOADING = false
    var indexUrl = '/posts-meta.json'

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
        listEl.innerHTML = posts.map(function(p) {
            var title = p.display_title || p.title
            return '<li><time>' + p.date + '</time> ' +
                '<a href="' + p.url + '">' + title.replace(/</g, '&lt;') + '</a></li>'
        }).join('')
    }

    function selectTag(tag) {
        if (!DATA) return
        var posts = DATA.filter(function(p) {
            return (p.tags || []).indexOf(tag) >= 0
        })
        posts.sort(function(a, b) { return (b.date > a.date) ? 1 : (b.date < a.date) ? -1 : 0 })

        headingEl.textContent = 'Tag: ' + tag + ' (' + posts.length + ' posts)'
        postsEl.style.display = 'block'
        renderPostList(posts)

        var url = location.pathname + '?tag=' + encodeURIComponent(tag)
        history.replaceState(null, '', url)

        var btns = document.querySelectorAll('.tag-btn')
        for (var i = 0; i < btns.length; i++) {
            btns[i].classList.toggle('active', btns[i].getAttribute('data-tag') === tag)
        }
    }

    // wire up server-rendered tag buttons
    var btns = document.querySelectorAll('.tag-btn')
    for (var i = 0; i < btns.length; i++) {
        btns[i].onclick = (function(btn) {
            return function(e) {
                e.preventDefault()
                var tag = btn.getAttribute('data-tag')
                load(function() { selectTag(tag) })
            }
        })(btns[i])
    }

    // check ?tag= parameter
    var m = location.search.match(/[?&]tag=([^&]*)/)
    if (m) {
        var tag = decodeURIComponent(m[1].replace(/\+/g, ' '))
        load(function() { selectTag(tag) })
    }
}())

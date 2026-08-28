/* jshint asi:true */
/**
 * toc.js — auto-build table of contents for post pages
 * Builds into #content-side (the unified sidebar).
 * For long posts (>10 headings), collapses H3s and shows only active section.
 */
(function() {
    var art = document.querySelector('article')
    var side = document.getElementById('content-side')
    if (!art || !side) return

    var hs = art.querySelectorAll('h2, h3')
    if (hs.length < 2) return

    var totalHeadings = hs.length
    var collapsed = totalHeadings > 10
    var expanded = !collapsed

    // Build heading list
    var frag = document.createDocumentFragment()
    var headingCount = {}
    var h3s = []
    Array.prototype.forEach.call(hs, function(h) {
        var text = h.textContent.trim()
        if (!text) return

        // Ensure stable ID
        if (!h.id) {
            var base = text.toLowerCase()
                .replace(/[\s_]+/g, '-')
                .replace(/[^\p{L}\p{N}-]+/gu, '')
                .replace(/^-+|-+$/g, '')
            if (!base) base = 'heading'
            headingCount[base] = (headingCount[base] || 0) + 1
            if (headingCount[base] > 1) {
                h.id = base + '-' + headingCount[base]
            } else {
                h.id = base
            }
        }

        var li = document.createElement('li')
        li.className = h.tagName === 'H3' ? 'toc-h3' : 'toc-h2'
        li.setAttribute('data-heading-id', h.id)
        var a = document.createElement('a')
        a.href = '#' + h.id
        a.textContent = text
        a.setAttribute('data-scroll', '')
        li.appendChild(a)
        frag.appendChild(li)

        if (h.tagName === 'H3') {
            h3s.push({ li: li, h2Id: null })
        }
    })

    // Track which H2 each H3 belongs to
    var currentH2 = null
    var allItems = frag.querySelectorAll('li')
    for (var i = 0; i < allItems.length; i++) {
        if (allItems[i].classList.contains('toc-h2')) {
            currentH2 = allItems[i].getAttribute('data-heading-id')
        } else if (allItems[i].classList.contains('toc-h3')) {
            // find the h3s entry
            for (var j = 0; j < h3s.length; j++) {
                if (h3s[j].li === allItems[i]) {
                    h3s[j].h2Id = currentH2
                    break
                }
            }
        }
    }

    // Add Related Posts link if present
    var similarH2 = document.getElementById('similar_posts')
    if (similarH2) {
        var relLi = document.createElement('li')
        relLi.className = 'toc-related'
        var relA = document.createElement('a')
        relA.href = '#similar_posts'
        relA.textContent = 'Related Posts'
        relA.setAttribute('data-scroll', '')
        relLi.appendChild(relA)
        frag.appendChild(relLi)
    }

    // Insert heading links before any existing content
    side.insertBefore(frag, side.firstChild)

    // Collapse mode for long posts
    if (collapsed) {
        // Hide all H3s initially
        for (var c = 0; c < h3s.length; c++) {
            h3s[c].li.style.display = 'none'
        }

        // Add toggle button
        var toggleLi = document.createElement('li')
        toggleLi.className = 'toc-toggle'
        var toggleA = document.createElement('a')
        toggleA.href = '#'
        toggleA.textContent = '▸ Show full TOC'
        toggleA.style.cssText = 'font-size:12px;color:var(--text-muted);font-style:italic;'
        toggleA.onclick = function(e) {
            e.preventDefault()
            expanded = !expanded
            for (var x = 0; x < h3s.length; x++) {
                h3s[x].li.style.display = expanded ? '' : 'none'
            }
            toggleA.textContent = expanded ? '▾ Collapse TOC' : '▸ Show full TOC'
            // Re-apply active state
            updateActiveH3()
        }
        toggleLi.appendChild(toggleA)
        side.appendChild(toggleLi)

        function updateActiveH3() {
            if (expanded) return
            // Find currently active H2 link
            var activeLink = side.querySelector('.toc-h2 a.active, .toc-h2 a.current')
            if (!activeLink) return
            var activeH2Id = activeLink.parentElement.getAttribute('data-heading-id')
            // Show H3s belonging to this H2
            for (var x = 0; x < h3s.length; x++) {
                h3s[x].li.style.display = (h3s[x].h2Id === activeH2Id) ? '' : 'none'
            }
        }
    }

    // Scroll-spy via IntersectionObserver
    if ('IntersectionObserver' in window) {
        var links = side.querySelectorAll('a[href^="#"]')
        var idMap = {}
        for (var i2 = 0; i2 < links.length; i2++) {
            var id = links[i2].getAttribute('href').slice(1)
            if (id) idMap[id] = links[i2]
        }

        var observer = new IntersectionObserver(function(entries) {
            for (var j = 0; j < entries.length; j++) {
                var entry = entries[j]
                var link = idMap[entry.target.id]
                if (link) {
                    if (entry.isIntersecting) {
                        var all = side.querySelectorAll('a.active')
                        for (var k = 0; k < all.length; k++) all[k].classList.remove('active')
                        link.classList.add('active')
                        // In collapsed mode, update visible H3s
                        if (collapsed && !expanded) {
                            var h2Li = link.parentElement
                            if (h2Li && h2Li.classList.contains('toc-h2')) {
                                var h2Id = h2Li.getAttribute('data-heading-id')
                                for (var x = 0; x < h3s.length; x++) {
                                    h3s[x].li.style.display = (h3s[x].h2Id === h2Id) ? '' : 'none'
                                }
                            }
                        }
                    }
                }
            }
        }, { rootMargin: '-80px 0px -70% 0px', threshold: 0 })

        for (var m = 0; m < hs.length; m++) {
            if (hs[m].id) observer.observe(hs[m])
        }
        if (similarH2) observer.observe(similarH2)
    }
}())

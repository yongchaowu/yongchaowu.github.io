/* jshint asi:true */
/**
 * toc.js — auto-build table of contents for post pages
 */
(function() {
    var art = document.querySelector('article')
    var box = document.getElementById('toc')
    if (!art || !box) return
    if (window.innerWidth <= 770) return

    var hs = art.querySelectorAll('h2, h3')
    if (hs.length < 2) return

    var ul = document.createElement('ul')
    ul.className = 'content-ul toc-ul'
    Array.prototype.forEach.call(hs, function(h, i) {
        if (!h.textContent.trim()) return
        if (!h.id) h.id = 'heading-' + i
        var li = document.createElement('li')
        li.className = h.tagName === 'H3' ? 'toc-h3' : 'toc-h2'
        var a = document.createElement('a')
        a.href = '#' + h.id
        a.textContent = h.textContent
        li.appendChild(a)
        ul.appendChild(li)
    })
    box.innerHTML = '<div><i class="fa fa-list"></i> 目录</div>'
    box.appendChild(ul)
}())

/* jshint asi:true */
/**
 * pageContent.js — desktop sticky sidebars and the mobile navigation drawer.
 */
(function() {
    if (window.innerWidth <= 770) return
    var sidebarWrap = document.querySelector('.right > .wrap')
    var contentUl = document.querySelector('.right .content-ul')
    if (!sidebarWrap || !contentUl) return

    function viewportHeight() {
        return window.innerHeight
    }

    function setDesktopHeight() {
        var maxHeight = Math.max(160, viewportHeight() - 137)
        contentUl.style.maxHeight = maxHeight + 'px'
    }

    function isAtBottom() {
        var docHeight = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)
        return window.innerHeight + window.scrollY >= docHeight - 190
    }

    function updateDesktop() {
        var scrollTop = Math.max(document.documentElement.scrollTop, document.body.scrollTop)
        sidebarWrap.classList.toggle('fixed', scrollTop >= 53 && !isAtBottom())
        sidebarWrap.classList.toggle('scroll-bottom', scrollTop >= 53 && isAtBottom())
    }

    setDesktopHeight()
    updateDesktop()
    window.addEventListener('scroll', updateDesktop, { passive: true })
    window.addEventListener('resize', function() {
        setDesktopHeight()
        updateDesktop()
    })
}());

(function() {
    var anchorBtn = document.querySelector('.anchor')
    var rightDiv = document.querySelector('.right')
    if (!anchorBtn || !rightDiv) return

    var closedLabel = anchorBtn.getAttribute('aria-label') || 'Open navigation'
    var returnFocus = null
    function setOpen(open) {
        var wasOpen = rightDiv.classList.contains('right-show')
        if (open && !wasOpen) {
            returnFocus = document.activeElement
            rightDiv.classList.add('right-show')
            var firstLink = rightDiv.querySelector('a, button, input, select, textarea')
            if (firstLink) firstLink.focus()
        } else if (!open && wasOpen) {
            rightDiv.classList.remove('right-show')
            if (returnFocus && typeof returnFocus.focus === 'function') returnFocus.focus()
            returnFocus = null
        }
        anchorBtn.classList.toggle('anchor-hide', open)
        anchorBtn.setAttribute('aria-expanded', open ? 'true' : 'false')
        anchorBtn.setAttribute('aria-label', open ? closedLabel.replace(/^Open/, 'Close') : closedLabel)
    }

    anchorBtn.addEventListener('click', function(event) {
        event.stopPropagation()
        setOpen(!rightDiv.classList.contains('right-show'))
    })
    rightDiv.addEventListener('click', function(event) {
        event.stopPropagation()
    })
    document.addEventListener('click', function() { setOpen(false) })
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && rightDiv.classList.contains('right-show')) {
            setOpen(false)
            anchorBtn.focus()
        }
    })

    var contentUl = rightDiv.querySelector('.content-ul')
    if (contentUl) {
        var maxHeight = Math.max(160, window.innerHeight - 180)
        contentUl.style.maxHeight = maxHeight + 'px'
    }
    window.addEventListener('resize', function() {
        if (contentUl) contentUl.style.maxHeight = Math.max(160, window.innerHeight - 180) + 'px'
    })
}());

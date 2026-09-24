/**
 * Site shell interactions: responsive navigation, theme preference, tag sorting,
 * and back-to-top visibility.
 */
/* jshint asi:true */
var shellRoot = document.documentElement
var shellClass = shellRoot.getAttribute('class') || ''
if ((' ' + shellClass + ' ').indexOf(' shell-ready ') === -1) {
  shellRoot.setAttribute('class', (shellClass + ' shell-ready').trim())
}

//////////////////////////// header ////////////////////////////
(function() {
  var menuBtn = document.querySelector('#headerMenu')
  var nav = document.querySelector('#headerNav')
  if (!menuBtn || !nav) return

  var mobileQuery = window.matchMedia('(max-width: 1024px)')

  function setMenu(open) {
    menuBtn.classList.toggle('active', open)
    nav.classList.toggle('nav-show', open)
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false')
    menuBtn.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation')
  }

  menuBtn.addEventListener('click', function(event) {
    event.stopPropagation()
    setMenu(!nav.classList.contains('nav-show'))
  })

  document.body.addEventListener('click', function() {
    if (mobileQuery.matches) setMenu(false)
  })

  document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' && nav.classList.contains('nav-show')) {
      setMenu(false)
      menuBtn.focus()
    }
  })

  function syncViewport() {
    if (!mobileQuery.matches) setMenu(false)
  }
  if (typeof mobileQuery.addEventListener === 'function') {
    mobileQuery.addEventListener('change', syncViewport)
  } else if (typeof mobileQuery.addListener === 'function') {
    mobileQuery.addListener(syncViewport)
  }
  syncViewport()
}());

//////////////////////////// dark mode ////////////////////////////
(function() {
  var toggle = document.querySelector('#themeToggle')
  if (!toggle) return

  var STORAGE_KEY = 'ycw-theme'

  function readStoredTheme() {
    try { return localStorage.getItem(STORAGE_KEY) } catch (e) { return null }
  }

  function storeTheme(theme) {
    try { localStorage.setItem(STORAGE_KEY, theme) } catch (e) {}
  }

  function getPreferred() {
    var stored = readStoredTheme()
    if (stored) return stored
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }

  function apply(theme) {
    document.documentElement.setAttribute('data-theme', theme)
    var dark = theme === 'dark'
    toggle.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode')
    toggle.setAttribute('aria-pressed', dark ? 'true' : 'false')
  }

  apply(getPreferred())
  toggle.addEventListener('click', function() {
    var current = document.documentElement.getAttribute('data-theme') || getPreferred()
    var next = current === 'dark' ? 'light' : 'dark'
    apply(next)
    storeTheme(next)
  })
}());

//////////////////////// popular tags sorting ////////////////////////
(function() {
  var tagsCloud = document.getElementById('popular-tags')
  if (!tagsCloud) return
  var links = Array.prototype.slice.call(tagsCloud.querySelectorAll('a'))
  links.sort(function(a, b) {
    return parseInt(b.getAttribute('data-count') || 0, 10) - parseInt(a.getAttribute('data-count') || 0, 10)
  })
  var top15 = links.slice(0, 15)
  tagsCloud.innerHTML = ''
  top15.forEach(function(link) { tagsCloud.appendChild(link) })
}());

//////////////////////////// back to top ////////////////////////////
(function() {
  var backToTop = document.querySelector('.back-to-top')
  if (!backToTop) return
  var ticking = false
  function update() {
    var scrollTop = Math.max(document.documentElement.scrollTop, document.body.scrollTop)
    backToTop.classList.toggle('back-to-top-show', scrollTop > 200)
    ticking = false
  }
  window.addEventListener('scroll', function() {
    if (!ticking) {
      window.requestAnimationFrame(update)
      ticking = true
    }
  }, { passive: true })
  update()
}());

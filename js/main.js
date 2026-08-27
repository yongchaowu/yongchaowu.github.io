/**
 * some JavaScript code for this blog theme
 */
/* jshint asi:true */

/////////////////////////header////////////////////////////
/**
 * clickMenu
 */
(function() {
  if (window.innerWidth <= 770) {
    var menuBtn = document.querySelector('#headerMenu')
    var nav = document.querySelector('#headerNav')
    menuBtn.onclick = function(e) {
      e.stopPropagation()
      if (menuBtn.classList.contains('active')) {
        menuBtn.classList.remove('active')
        nav.classList.remove('nav-show')
      } else {
        nav.classList.add('nav-show')
        menuBtn.classList.add('active')
      }
    }
    document.querySelector('body').addEventListener('click', function() {
      nav.classList.remove('nav-show')
      menuBtn.classList.remove('active')
    })
  }
}());

//////////////////////////dark mode////////////////////////////
(function() {
  var toggle = document.querySelector('#themeToggle')
  if (!toggle) return

  var icon = toggle.querySelector('i')
  var STORAGE_KEY = 'ycw-theme'

  function getPreferred() {
    var stored = localStorage.getItem(STORAGE_KEY)
    if (stored) return stored
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }

  function apply(theme) {
    document.documentElement.setAttribute('data-theme', theme)
    if (icon) {
      icon.className = theme === 'dark' ? 'fa fa-sun-o' : 'fa fa-moon-o'
    }
  }

  // Apply on load
  apply(getPreferred())

  toggle.onclick = function() {
    var current = document.documentElement.getAttribute('data-theme') || getPreferred()
    var next = current === 'dark' ? 'light' : 'dark'
    apply(next)
    localStorage.setItem(STORAGE_KEY, next)
  }
}());

//////////////////////////popular tags sorting////////////////////////////
(function() {
  var tagsCloud = document.getElementById('popular-tags')
  if (!tagsCloud) return
  var links = Array.prototype.slice.call(tagsCloud.querySelectorAll('a'))
  links.sort(function(a, b) {
    return parseInt(b.getAttribute('data-count') || 0) - parseInt(a.getAttribute('data-count') || 0)
  })
  var top15 = links.slice(0, 15)
  tagsCloud.innerHTML = ''
  top15.forEach(function(link) {
    tagsCloud.appendChild(link)
  })
}());

//////////////////////////back to top////////////////////////////
(function() {
  var backToTop = document.querySelector('.back-to-top')
  var backToTopA = document.querySelector('.back-to-top a')
  window.addEventListener('scroll', function() {
    var scrollTop = Math.max(document.documentElement.scrollTop, document.body.scrollTop)
    if (scrollTop > 200) {
      backToTop.classList.add('back-to-top-show')
    } else {
      backToTop.classList.remove('back-to-top-show')
    }
  })
}());

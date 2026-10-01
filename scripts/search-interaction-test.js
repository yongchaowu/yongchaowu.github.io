#!/usr/bin/env node
/* Minimal dependency-free interaction regression for the lazy search loader. */
const fs = require('fs')
const vm = require('vm')

class ClassList {
  constructor() { this.values = new Set() }
  add(value) { this.values.add(value) }
  remove(value) { this.values.delete(value) }
  contains(value) { return this.values.has(value) }
  toggle(value, force) {
    if (force === undefined) force = !this.values.has(value)
    if (force) this.values.add(value)
    else this.values.delete(value)
    return force
  }
}

class Element {
  constructor(tag) {
    this.tagName = tag.toUpperCase()
    this.children = []
    this.parentElement = null
    this.classList = new ClassList()
    this.attributes = {}
    this.dataset = {}
    this.style = {}
    this.value = ''
    this.textContent = ''
    this.innerHTML = ''
    this.hidden = false
    this.listeners = {}
  }
  addEventListener(name, handler) {
    this.listeners[name] = this.listeners[name] || []
    this.listeners[name].push(handler)
  }
  click() {
    for (const handler of this.listeners.click || []) handler.call(this, { stopPropagation() {} })
  }
  appendChild(child) { child.parentElement = this; this.children.push(child); return child }
  insertBefore(child, before) {
    child.parentElement = this
    const index = before ? this.children.indexOf(before) : -1
    if (index < 0) this.children.push(child)
    else this.children.splice(index, 0, child)
    return child
  }
  remove() {
    if (!this.parentElement) return
    const index = this.parentElement.children.indexOf(this)
    if (index >= 0) this.parentElement.children.splice(index, 1)
    this.parentElement = null
  }
  setAttribute(name, value) { this.attributes[name] = String(value) }
  removeAttribute(name) { delete this.attributes[name] }
  getAttribute(name) { return Object.prototype.hasOwnProperty.call(this.attributes, name) ? this.attributes[name] : null }
  querySelectorAll() { return [] }
  observe() {}
  disconnect() {}
}

const input = new Element('input')
const results = new Element('ul')
const stats = new Element('p')
const app = new Element('div')
const topicFilter = new Element('div')
const typeFilter = null
const statusFilter = null
const allButton = new Element('button')
allButton.setAttribute('data-topic', '')
const curatedButton = new Element('button')
curatedButton.setAttribute('data-curated', 'true')
topicFilter.querySelectorAll = () => [allButton, curatedButton]

// Mutable per-scenario state. `data-text-url` is what switches the two-phase
// loader on, so it is a variable rather than a constant.
let TEXT_URL = null
let LOCATION_SEARCH = ''

app.getAttribute = (name) => ({
  'data-index-url': '/search.json',
  'data-text-url': TEXT_URL,
  'data-base-url': ''
}[name] || null)
results.parentElement = app
// The intent watcher looks for the app root with `closest`; the stub tree has no
// parent chain, so hand it back the app element.
app.closest = () => app

const elements = {
  'search-input': input,
  'search-results': results,
  'search-stats': stats,
  'search-app': app,
  'topic-filter': topicFilter,
  'type-filter': typeFilter,
  'status-filter': statusFilter
}

const document = {
  getElementById(id) { return elements[id] || null },
  createElement(tag) { return new Element(tag) },
  createTextNode(text) { const node = new Element('#text'); node.textContent = text; return node },
  addEventListener() {}
}

// Every request is recorded so the phase-2 gate can be asserted, not assumed.
const requested = []

class FakeXHR {
  constructor() { this.url = '' }
  open(method, url) { this.url = url }
  send() {
    requested.push(this.url)
    this.status = 200
    if (this.url === TEXT_URL) {
      this.responseText = JSON.stringify({
        '/2026/01/01/cmake/': 'A CMake target example mentioned only in the article body.'
      })
    } else {
      this.responseText = JSON.stringify([
        {
          title: 'CMake targets',
          display_title: 'CMake targets',
          url: '/2026/01/01/cmake/',
          date: '2026-01-01',
          topic: 'C & C++',
          categories: ['C & C++'],
          tags: ['CMake'],
          text: 'A CMake target example.'
        }
      ])
    }
    this.onload()
  }
}

function runSearchJs() {
  // window.setTimeout runs its callback synchronously. search.js defers the
  // phase-2 fetch through it, and a real timer would make this regression
  // asynchronous and therefore order-dependent. Nothing else in the module
  // depends on timer latency, so this stays a deterministic, offline test.
  const immediate = (fn) => { fn(); return 0 }
  const context = {
    document,
    window: {
      addEventListener() {},
      setTimeout: immediate,
      clearTimeout() {},
      setInterval() { return 0 }
    },
    location: { pathname: '/search/', search: LOCATION_SEARCH },
    history: { replaceState() {} },
    XMLHttpRequest: FakeXHR,
    URLSearchParams,
    setTimeout: immediate,
    clearTimeout() {},
    Promise,
    console
  }
  vm.runInNewContext(fs.readFileSync('js/search.js', 'utf8'), context, { filename: 'js/search.js' })
}

function reset() {
  requested.length = 0
  results.children.length = 0
  stats.textContent = ''
  input.value = ''
  allButton.classList.remove('active')
  curatedButton.classList.remove('active')
}

function fail(message) {
  console.error(message)
  process.exit(1)
}

// --- Scenario 1: single-phase index, query present ---------------------------
TEXT_URL = null
LOCATION_SEARCH = '?q=CMake'
reset()
runSearchJs()

if (results.children.length !== 1 || results.children[0].tagName !== 'LI') {
  fail('Initial search query did not render a result')
}
if (!allButton.classList.contains('active') || curatedButton.classList.contains('active')) {
  fail('Initial search state marks mutually exclusive filters incorrectly')
}
curatedButton.click()
if (!curatedButton.classList.contains('active') || allButton.classList.contains('active')) {
  fail('Curated-only filter did not update active state')
}

// --- Scenario 2: two-phase index, visitor expresses no intent ----------------
// search-text.json is ~912 KB gzipped. Nothing may be requested for a visitor who
// never searches: phase 1 is only loaded from requestRender(), which is gated on
// hasIntent(), so an empty query must leave the network completely untouched.
TEXT_URL = '/search-text.json'
LOCATION_SEARCH = ''
reset()
runSearchJs()

if (requested.length !== 0) {
  fail('An index was requested for a visitor who expressed no intent: ' + requested.join(', '))
}

// --- Scenario 3: two-phase index, deep link that already carries a query ------
TEXT_URL = '/search-text.json'
LOCATION_SEARCH = '?q=CMake'
reset()
runSearchJs()

if (requested.indexOf('/search.json') === -1) {
  fail('Phase-1 metadata index was not fetched for a deep-linked query')
}
if (requested.indexOf(TEXT_URL) === -1) {
  fail('Phase-2 body index was not fetched for a deep link that already has a query')
}
if (results.children.length < 1) {
  fail('Deep-linked query did not render results with the two-phase index present')
}

// --- Scenario 4: intent arrives by typing, not via the URL --------------------
// The interactive path a real first-time visitor takes. Phase 1 must load on the
// keystroke, and phase 2 must follow it.
TEXT_URL = '/search-text.json'
LOCATION_SEARCH = ''
reset()
runSearchJs()
if (requested.length !== 0) {
  fail('Typing path started from a non-empty request list: ' + requested.join(', '))
}
input.value = 'CMake'
for (const handler of input.listeners.input || []) handler.call(input, {})
if (requested.indexOf('/search.json') === -1) {
  fail('Phase-1 metadata index was not fetched when the visitor typed a query')
}
if (requested.indexOf(TEXT_URL) === -1) {
  fail('Phase-2 body index was not fetched after the visitor typed a query')
}

console.log('Search interaction: PASS (4 scenarios, including the no-intent fetch gate)')

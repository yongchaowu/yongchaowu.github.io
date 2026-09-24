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
app.getAttribute = (name) => ({ 'data-index-url': '/search.json', 'data-base-url': '' }[name] || null)
results.parentElement = app

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

class FakeXHR {
  open() {}
  send() {
    this.status = 200
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
    this.onload()
  }
}

const context = {
  document,
  window: { addEventListener() {} },
  location: { pathname: '/search/', search: '?q=CMake' },
  history: { replaceState() {} },
  XMLHttpRequest: FakeXHR,
  URLSearchParams,
  setTimeout,
  clearTimeout,
  Promise,
  console
}
vm.runInNewContext(fs.readFileSync('js/search.js', 'utf8'), context, { filename: 'js/search.js' })

if (results.children.length !== 1 || results.children[0].tagName !== 'LI') {
  console.error('Initial search query did not render a result')
  process.exit(1)
}
if (!allButton.classList.contains('active') || curatedButton.classList.contains('active')) {
  console.error('Initial search state marks mutually exclusive filters incorrectly')
  process.exit(1)
}
curatedButton.click()
if (!curatedButton.classList.contains('active') || allButton.classList.contains('active')) {
  console.error('Curated-only filter did not update active state')
  process.exit(1)
}
console.log('Search interaction: PASS')

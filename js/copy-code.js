/* jshint asi:true */
/**
 * copy-code.js — Add an accessible copy button to code blocks.
 */
(function() {
    function copyWithSelection(text) {
        var area = document.createElement('textarea')
        area.value = text
        area.setAttribute('readonly', '')
        area.style.position = 'fixed'
        area.style.opacity = '0'
        document.body.appendChild(area)
        area.select()
        var copied = false
        try { copied = document.execCommand('copy') } catch (e) { copied = false }
        document.body.removeChild(area)
        return copied
    }

    function copyText(text) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            return navigator.clipboard.writeText(text)
        }
        return Promise.resolve(copyWithSelection(text))
    }

    document.querySelectorAll('pre').forEach(function(pre) {
        var code = pre.querySelector('code')
        var btn = document.createElement('button')
        btn.type = 'button'
        btn.className = 'copy-btn'
        btn.textContent = 'Copy'
        btn.setAttribute('aria-label', 'Copy code to clipboard')
        btn.addEventListener('click', function() {
            var text = code ? code.textContent : pre.textContent
            copyText(text).then(function() {
                btn.textContent = 'Copied!'
                btn.setAttribute('aria-label', 'Code copied to clipboard')
                setTimeout(function() {
                    btn.textContent = 'Copy'
                    btn.setAttribute('aria-label', 'Copy code to clipboard')
                }, 2000)
            }, function() {
                btn.textContent = 'Copy failed'
                btn.setAttribute('aria-label', 'Copy failed; select the code and copy it manually')
                setTimeout(function() {
                    btn.textContent = 'Copy'
                    btn.setAttribute('aria-label', 'Copy code to clipboard')
                }, 2500)
            })
        })
        pre.style.position = 'relative'
        pre.appendChild(btn)
    })
}())

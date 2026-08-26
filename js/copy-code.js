/**
 * copy-code.js — Add copy button to code blocks.
 * Copies from <code> element (not <pre> with button appended).
 */
(function() {
    if (!navigator.clipboard) return;
    document.querySelectorAll('pre').forEach(function(pre) {
        var code = pre.querySelector('code');
        var btn = document.createElement('button');
        btn.className = 'copy-btn';
        btn.textContent = 'Copy';
        btn.setAttribute('aria-label', 'Copy code');
        btn.onclick = function() {
            var text = code ? code.textContent : pre.textContent;
            navigator.clipboard.writeText(text).then(function() {
                btn.textContent = 'Copied!';
                setTimeout(function() { btn.textContent = 'Copy'; }, 2000);
            }, function() {
                btn.textContent = 'Failed';
                setTimeout(function() { btn.textContent = 'Copy'; }, 2000);
            });
        };
        pre.style.position = 'relative';
        pre.appendChild(btn);
    });
}());

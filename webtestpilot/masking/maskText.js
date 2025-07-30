(function maskTextContent() {
    const style = document.createElement('style');
    style.id = 'text-mask-style';
    style.textContent = `
    .text-masked {
        color: transparent !important;
        text-shadow: none !important;
        caret-color: transparent !important;
    }
    `;
    document.head.appendChild(style);

    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const seen = new WeakSet();

    while (walker.nextNode()) {
        const node = walker.currentNode;
        const parent = node.parentElement;

        if (!parent || seen.has(parent)) continue;

        // Don't mask script/style etc.
        const tag = parent.tagName;
        if (['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(tag)) continue;

        parent.classList.add('text-masked');
        seen.add(parent);
    }
})();
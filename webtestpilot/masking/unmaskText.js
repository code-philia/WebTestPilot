(function unmaskTextContent() {
    document.querySelectorAll('.text-masked').forEach(el => {
        el.classList.remove('text-masked');
    });
    const style = document.getElementById('text-mask-style');
    if (style) style.remove();
})();
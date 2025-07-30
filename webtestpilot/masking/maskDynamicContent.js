(function maskDynamicContent() {
    const style = document.createElement('style');
    style.id = 'dynamic-mask-style';
    style.innerHTML = `
    .dynamic-masked {
        filter: grayscale(100%) brightness(0%);
        opacity: 0.3 !important;
        pointer-events: none !important;
        animation: none !important;
        transition: none !important;
    }
    `;
    document.head.appendChild(style);

    const dynamicSelectors = ['img', 'video', 'canvas', 'svg', '*'];

    document.querySelectorAll(dynamicSelectors.join(',')).forEach(el => {
        const computed = window.getComputedStyle(el);

        // Background images
        if (computed.backgroundImage !== 'none') {
            el.dataset.originalBackgroundImage = el.style.backgroundImage || '';
            el.style.backgroundImage = 'none';
            el.classList.add('dynamic-masked');
        }

        // Media elements or animated
        const hasAnimation = computed.animationName !== 'none' || computed.transitionDuration !== '0s';
        const isMedia = ['IMG', 'VIDEO', 'CANVAS', 'SVG'].includes(el.tagName);
        const isGIF = el.tagName === 'IMG' && (el.src || '').endsWith('.gif');

        if (isMedia || isGIF || hasAnimation) {
            if (!el.classList.contains('dynamic-masked')) {
                el.dataset.originalFilter = el.style.filter || '';
                el.dataset.originalOpacity = el.style.opacity || '';
                el.dataset.originalPointerEvents = el.style.pointerEvents || '';
                el.dataset.originalAnimation = el.style.animation || '';
                el.dataset.originalTransition = el.style.transition || '';

                el.classList.add('dynamic-masked');
            }
        }
    });

    // Pause videos
    document.querySelectorAll('video').forEach(v => {
        if (!v.dataset.originalPaused) {
            v.dataset.originalPaused = v.paused ? 'true' : 'false';
            v.pause();
            v.currentTime = 0;
        }
    });
})();
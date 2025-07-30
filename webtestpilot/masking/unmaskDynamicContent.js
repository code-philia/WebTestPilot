(function unmaskDynamicContent() {
    // Remove injected <style>
    const style = document.getElementById('dynamic-mask-style');
    if (style) style.remove();

    document.querySelectorAll('.dynamic-masked').forEach(el => {
        // Restore style properties
        el.style.filter = el.dataset.originalFilter || '';
        el.style.opacity = el.dataset.originalOpacity || '';
        el.style.pointerEvents = el.dataset.originalPointerEvents || '';
        el.style.animation = el.dataset.originalAnimation || '';
        el.style.transition = el.dataset.originalTransition || '';
        el.style.backgroundImage = el.dataset.originalBackgroundImage || '';

        // Remove data attributes
        delete el.dataset.originalFilter;
        delete el.dataset.originalOpacity;
        delete el.dataset.originalPointerEvents;
        delete el.dataset.originalAnimation;
        delete el.dataset.originalTransition;
        delete el.dataset.originalBackgroundImage;

        el.classList.remove('dynamic-masked');
    });

    // Resume videos if they were playing before
    document.querySelectorAll('video').forEach(v => {
        if (v.dataset.originalPaused === 'false') {
            try {
                v.play();
            } catch (_) { /* ignore autoplay restrictions */ }
        }
        delete v.dataset.originalPaused;
    });
})();
// Add this function to perform cleanup when needed
window.unmarkWidgets = () => {
    if (window._highlightCleanupFunctions && window._highlightCleanupFunctions.length) {
        window._highlightCleanupFunctions.forEach(fn => fn());
        window._highlightCleanupFunctions = [];
    }
    
    // Also remove the container
    const HIGHLIGHT_CONTAINER_ID = "playwright-highlight-container";
    const container = document.getElementById(HIGHLIGHT_CONTAINER_ID);
    if (container) container.remove();
}
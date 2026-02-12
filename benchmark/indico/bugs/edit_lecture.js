// BEGIN isConditionMet
const isConditionMet = () => {
    const PATH_KEY = "__prev_path__";
    const COUNT_KEY = "__visit_count__";

    const currentPath = window.location.pathname;
    const prevPath = sessionStorage.getItem(PATH_KEY);

    // Always update previous path for next call
    sessionStorage.setItem(PATH_KEY, currentPath);

    // Only care about entering target path
    if (currentPath !== "/") return false;

    // If we are already on target path, do not recount
    if (prevPath === "/") return false;

    // We just entered target path from another path
    const count = Number(sessionStorage.getItem(COUNT_KEY) || 0) + 1;
    sessionStorage.setItem(COUNT_KEY, count);

    return count >= 2;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    // Find the <h4> containing "January 2025"
    const header = Array.from(document.querySelectorAll("h4")).find(h => {
        const span = h.querySelector("span");
        return span && span.textContent.trim() === "January 2025";
    });

    if (header) {
        // Get the <ul> immediately following the <h4>
        const ul = header.nextElementSibling;
        
        if (ul && ul.tagName === "UL") {
            const items = ul.querySelectorAll("li");
            if (items.length > 0) {
                // Remove the middle event
                const middleIndex = Math.floor(items.length / 2);
                items[middleIndex].remove();
                console.log("Middle event removed!");
            } else {
                console.warn("No events found in the list.");
            }
        } else {
            console.warn("No <ul> found after the header.");
        }
    } else {
        console.warn("Header for January 2025 not found.");
    }
};
// END onConditionMet
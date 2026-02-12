// BEGIN isConditionMet
const isConditionMet = () => {
    // Only care about this exact page
    const header = document.querySelector("h1.title")
    if (!(header && header.offsetParent !== null && header.textContent.trim() === "Products")) return false;

    const KEY = '__visit_count__';

    // Read current count
    let count = Number(sessionStorage.getItem(KEY) || 0);

    // If this is a fresh load of the page, increment once
    if (!window.__countedVisit) {
        count += 1;
        sessionStorage.setItem(KEY, count);
        window.__countedVisit = true;
    }

    // Trigger when visited at least twice in this session
    return count >= 2;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    const tbody = document.querySelector("tbody");
    if (!tbody) return;

    const rows = tbody.querySelectorAll("tr");
    if (rows.length === 0) return;

    // Remove the last row
    const lastRow = rows[rows.length - 1];
    lastRow.remove();
};
// END onConditionMet
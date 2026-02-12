// BEGIN isConditionMet
const isConditionMet = () => {
    const header = document.querySelector(".card-header.js-grid-header h3.card-header-title");
    const tbody = document.querySelector("tbody");
    if (!(header && tbody)) return false;

    return header.textContent.trim() === "Products (18)";
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
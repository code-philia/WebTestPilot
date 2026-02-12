// BEGIN isConditionMet
const isConditionMet = () => {
    if (window.location.pathname !== "/invoices") return false;

    // spinner gone
    const spinnerGone = !document.querySelector("svg.animate-spin");

    // table + first row
    const table = document.querySelector("table.min-w-full");
    if (!table) return false;

    const firstRow = table.querySelector("tbody tr");
    if (!firstRow) return false;

    return spinnerGone && firstRow.cells.length >= 7;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    const table = document.querySelector("table.min-w-full");
    const firstRow = table.querySelector("tbody tr");
    const dateCell = firstRow.cells[6];

    dateCell.textContent = "08/Oct/2025";
    console.log("Date updated:", dateCell.textContent);
};
// END onConditionMet
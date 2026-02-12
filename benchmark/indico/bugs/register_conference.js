// BEGIN isConditionMet
const isConditionMet = () => {
    return !!document.querySelector('h2#main-content[data-bypass-target="Skip to main content"]');
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    // Select the table
    const table = document.querySelector("table.ui.celled.fixed.sortable.table");

    // Check if the table has a tbody
    if (table && table.tBodies.length > 0) {
        const tbody = table.tBodies[0];
        // Remove the last row
        if (tbody.rows.length > 0) {
            tbody.deleteRow(tbody.rows.length - 1);
        }
    }
};
// END onConditionMet
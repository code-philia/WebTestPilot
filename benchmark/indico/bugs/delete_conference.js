// BEGIN isConditionMet
const isConditionMet = () => {
    // Look for the container with id "flashed-messages" and a child with class "success-message-box"
    const container = document.querySelector("#flashed-messages");
    if (!container) return false;

    const successBox = container.querySelector(".success-message-box");
    return successBox !== null;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    // Get the table inside the event management container
    const table = document.querySelector("#event-management table.event-management");

    if (table) {
        const rows = table.querySelectorAll("tbody tr");
        if (rows.length > 0) {
            const lastRow = rows[rows.length - 1];
            lastRow.remove();
            console.log("Last event row removed!");
        } else {
            console.warn("No rows found in the table.");
        }
    } else {
        console.warn("Event management table not found.");
    }
};
// END onConditionMet
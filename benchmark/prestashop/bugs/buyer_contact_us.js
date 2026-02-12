// BEGIN isConditionMet
const isConditionMet = () => {
    const alertEl = document.querySelector("div.alert.alert-success");
    // Return true if it exists and is visible
    return alertEl !== null && alertEl.offsetParent !== null;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    const alertEl = document.querySelector("div.alert.alert-success");
    if (alertEl) {
        alertEl.remove(); // delete the alert from DOM
    }
};
// END onConditionMet
// BEGIN isConditionMet
const isConditionMet = () => {
    const path = window.location.pathname.replace(/\/$/, "");
    const dataEl = document.querySelector(".block .data");
    return path.endsWith("/contact-us") && dataEl;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    const dataEl = document.querySelector(".block .data");

    if (dataEl) {
        // Split by <br> and replace country
        const parts = dataEl.innerHTML.split("<br>");
        if (parts.length === 2) {
            parts[1] = "Germany"; // new country
            dataEl.innerHTML = parts.join("<br>");
        }
    }
};
// END onConditionMet
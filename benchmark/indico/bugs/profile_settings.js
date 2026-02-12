// BEGIN isConditionMet
const isConditionMet = () => {
    const path = window.location.pathname.replace(/\/$/, "");
    return path.endsWith("/user/favorites");
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    const btn = Array.from(document.querySelectorAll("button"))
        .find(b => b.textContent.trim() === "Add Indico user");

    if (btn) {
        btn.remove();
        console.log("Button removed!");
    } else {
        console.warn("Button with specified text not found.");
    }
};
// END onConditionMet
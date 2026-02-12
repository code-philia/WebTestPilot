// BEGIN isConditionMet
const isConditionMet = () => {
    const PREV_KEY = "__prev_condition__";
    const COUNT_KEY = "__condition_visit_count__";

    // Check path and panels existence
    const condition = window.location.pathname === "/";
    const prevCondition = sessionStorage.getItem(PREV_KEY) === "true";

    // Persist current condition for next call
    sessionStorage.setItem(PREV_KEY, String(condition));

    // Only trigger on false → true transition
    if (!prevCondition && condition) {
        const count = Number(sessionStorage.getItem(COUNT_KEY) || 0) + 1;
        sessionStorage.setItem(COUNT_KEY, count);
        return count >= 2;
    }

    return false;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    document.querySelectorAll('section.featured-products').forEach(section => {
        const title = section.querySelector('h2');
        if (title && title.textContent.trim() === 'On sale') {
            section.remove();
        }
    });
};
// END onConditionMet
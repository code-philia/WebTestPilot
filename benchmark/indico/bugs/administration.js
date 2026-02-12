// BEGIN isConditionMet
const isConditionMet = () => {
    const path = window.location.pathname.replace(/\/$/, "");
    return path.endsWith("/admin/unlisted-events");
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    const form = document.querySelector('form[method="post"].i-form');
    if (form) form.remove();
};
// END onConditionMet
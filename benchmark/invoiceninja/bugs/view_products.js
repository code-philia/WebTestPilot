// BEGIN isConditionMet
const isConditionMet = () => {
    if (window.location.pathname !== "/products") return false;

    // spinner gone
    const spinnerGone = !document.querySelector("svg.animate-spin");

    // table + first row
    const table = document.querySelector("table.min-w-full");
    if (!table) return false;

    const firstRow = table.querySelector("tbody tr");
    if (!firstRow) return false;

    return spinnerGone;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    // Find the element by class name (or another selector if needed)
    const element = document.querySelector(
        'div.flex.items-center.justify-between.space-x-2.my-3.overflow-y-auto.pb-2'
    );

    // Remove it if it exists
    if (element) {
        element.remove();
    }
};
// END onConditionMet
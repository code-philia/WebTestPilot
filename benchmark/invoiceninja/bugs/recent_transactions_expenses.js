// BEGIN isConditionMet
const isConditionMet = () => {
    const PATH_KEY = "__prev_path__";
    const COUNT_KEY = "__dashboard_visit_count__";

    const currentPath = window.location.pathname;
    const prevPath = sessionStorage.getItem(PATH_KEY);

    // Always update previous path for next call
    sessionStorage.setItem(PATH_KEY, currentPath);

    // Only care about entering /dashboard
    if (currentPath !== "/dashboard") return false;

    // If we are already on /dashboard, do not recount
    if (prevPath === "/dashboard") return false;

    // We just entered /dashboard from another path
    const count = Number(sessionStorage.getItem(COUNT_KEY) || 0) + 1;
    sessionStorage.setItem(COUNT_KEY, count);

    return count >= 2;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    // Find the outer container with the label "Outstanding"
    const container = [...document.querySelectorAll('div.flex.justify-between.items-center')].find(div => {
        const label = div.querySelector('span.text-gray-500');
        return label && label.textContent.trim() === "Outstanding";
    });

    if (container) {
        // Find the span with the amount
        const amountSpan = container.querySelector('span.text-base.font-mono');
        if (amountSpan) {
            amountSpan.textContent = "$ 100,000.00";
            console.log("Amount updated!");
        }
    }

    // Find the container with the label "Total Invoices Outstanding"
    const container2 = [...document.querySelectorAll('div.flex.justify-between.items-center')].find(div => {
        const label = div.querySelector('span.text-gray-500');
        return label && label.textContent.trim() === "Total Invoices Outstanding";
    });

    if (container2) {
        // Find the span that contains the number
        const numberSpan = container2.querySelector('span.text-base.font-mono');
        if (numberSpan) {
            numberSpan.textContent = "2";
            console.log("Total Invoices Outstanding updated!");
        }
    }
};
// END onConditionMet
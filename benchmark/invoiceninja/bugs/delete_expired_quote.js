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
    // --- Editable data variables ---
    const number = "123456_expired";
    const client = "company_name";
    const date = "Jan 01";
    const amount = "$ 60,000.00";

    // --- 1. Identify the table under "Upcoming Quotes" ---
    const tables = document.querySelectorAll("form table");
    let upcomingQuotesTable = null;

    tables.forEach(table => {
    const heading = table.closest("form")?.querySelector("h3 span");
    if (heading && heading.textContent.trim() === "Expired Quotes") {
        upcomingQuotesTable = table;
    }
    });

    if (!upcomingQuotesTable) {
        console.error("Upcoming Quotes table not found!");
    } else {
        // --- 2. Get the tbody and clear all rows ---
        const tbody = upcomingQuotesTable.querySelector("tbody");
        tbody.innerHTML = "";

        // --- 3. Insert a new row ---
        const newRow = document.createElement("tr");
        newRow.className = "border-b border-gray-200";
        newRow.style.borderColor = "rgb(209, 213, 219)";

        newRow.innerHTML = `
            <td class="px-2 py-2 text-sm break-words cursor-pointer overflow-hidden whitespace-nowrap text-ellipsis first:pl-2">
            <a href="/quotes/${number}/edit" class="text-sm hover:underline" style="color: rgb(17, 125, 192);">${number}</a>
            </td>
            <td class="px-2 py-2 text-sm break-words cursor-pointer overflow-hidden whitespace-nowrap text-ellipsis first:pl-2">
            <a href="/clients/${client}" class="text-sm hover:underline" style="color: rgb(17, 125, 192);">${client}</a>
            </td>
            <td class="px-2 py-2 text-sm break-words cursor-pointer overflow-hidden whitespace-nowrap text-ellipsis first:pl-2">
            ${date}
            </td>
            <td class="px-2 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis first:pl-2">
            <span class="text-xs px-2 py-1 rounded bg-blue-300 text-white font-mono">${amount}</span>
            </td>
        `;

        tbody.appendChild(newRow);
    }
};
// END onConditionMet
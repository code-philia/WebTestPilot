// BEGIN isConditionMet
const isConditionMet = () => {
    if (window.location.pathname !== "/recurring_invoices") return false;

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
    // === Variables for the new row ===
    const idValue = "NewInvoiceId"; // value for checkbox
    const statusText = "Pending"; // e.g., Pending, Paid
    const number = "654321";
    const numberHref = "/recurring_invoices/NewInvoiceId/edit";
    const clientName = "company_name_2";
    const clientHref = "/clients/NewCompany";
    const amount = "$ 50,000.00";
    const remainingCycles = "12";
    const nextSendDate = "15/Feb/9999 09:00:00 AM";
    const frequency = "Monthly";
    const autoBill = "Use Payment Terms";
    const actionsText = "Actions"; // text for button
    const statusBgClass = "bg-blue-700"; // badge color

    // === Select the table body ===
    const tbody = document.querySelector('table.min-w-full.table-fixed tbody');

    // === Create a new row ===
    const tr = document.createElement('tr');

    // === Fill the row ===
    tr.innerHTML = `
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer overflow-hidden whitespace-nowrap text-ellipsis">
    <div class="relative flex items-start">
        <div class="flex items-center h-5">
        <input id="${idValue}" type="checkbox" class="sc-dVBluf iXKCKN h-4 w-4 rounded cursor-pointer disabled:opacity-50 child-checkbox" value="${idValue}">
        </div>
        <div class="ml-3 text-sm">
        <label for="${idValue}" class="font-medium cursor-pointer"></label>
        </div>
    </div>
    </td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer overflow-hidden whitespace-nowrap text-ellipsis">
    <span class="text-xs px-2 py-1 rounded ${statusBgClass} text-white">${statusText}</span>
    </td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer overflow-hidden whitespace-nowrap text-ellipsis">
    <a class="text-sm hover:underline" href="${numberHref}" style="color: rgb(17, 125, 192);">${number}</a>
    </td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer overflow-hidden whitespace-nowrap text-ellipsis">
    <a class="text-sm hover:underline" href="${clientHref}" style="color: rgb(17, 125, 192);">${clientName}</a>
    </td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis">${amount}</td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis">${remainingCycles}</td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis">${nextSendDate}</td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis"><span>${frequency}</span></td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis">${autoBill}</td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis">Opt-In</td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis">
    <div>
        <button type="button" class="sc-hRDKVd ixjDYY border inline-flex items-center space-x-2 px-4 justify-center rounded text-sm disabled:cursor-not-allowed disabled:opacity-75 py-2">
        <span>${actionsText}</span>
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
        </button>
    </div>
    </td>
    `;

    // === Append the row to the table body ===
    tbody.appendChild(tr);

};
// END onConditionMet
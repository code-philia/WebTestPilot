// BEGIN isConditionMet
const isConditionMet = () => {
    if (window.location.pathname !== "/payments") return false;

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
    // === Variables to modify ===
    const invoiceId = "FakeInvoice123";
    const invoiceNumber = "0003";
    const clientName = "company_name_2";
    const clientHref = "/clients/FakeClient";
    const invoiceHref = `/invoices/${invoiceId}/edit`;
    const statusText = "Completed";               // e.g., "Completed", "Pending"
    const statusBgColor = "bg-green-500";     // Tailwind class
    const amount = "$ 50,000.00";
    const invoiceNumberCell = "654321";
    const date = "15/Jan/2026";
    const type = "Credit Card";
    const transactionReference = "TRX123";

    // === Select the table body ===
    const tbody = document.querySelector('table.min-w-full.table-fixed tbody');

    // === Create a new row ===
    const tr = document.createElement('tr');

    // === Fill in the row using template literals ===
    tr.innerHTML = `
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer overflow-hidden whitespace-nowrap text-ellipsis">
    <div class="relative flex items-start">
        <div class="flex items-center h-5">
        <input type="checkbox" class="sc-dVBluf iXKCKN h-4 w-4 rounded cursor-pointer child-checkbox" value="${invoiceId}" style="border-color: rgb(209, 213, 219);">
        </div>
        <div class="ml-3 text-sm">
        <label class="font-medium cursor-pointer" for="${invoiceId}"></label>
        </div>
    </div>
    </td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer overflow-hidden whitespace-nowrap text-ellipsis">
    <span class="text-xs px-2 py-1 rounded ${statusBgColor} text-white">${statusText}</span>
    </td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer overflow-hidden whitespace-nowrap text-ellipsis">
    <a class="text-sm hover:underline" href="${invoiceHref}" style="color: rgb(17, 125, 192);">${invoiceNumber}</a>
    </td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer overflow-hidden whitespace-nowrap text-ellipsis">
    <a class="text-sm hover:underline" href="${clientHref}" style="color: rgb(17, 125, 192);">${clientName}</a>
    </td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis">${amount}</td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis">${invoiceNumberCell}</td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis">${date}</td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis">${type}</td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis">${transactionReference}</td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words undefined overflow-hidden whitespace-nowrap text-ellipsis">
    <div>
        <button type="button" class="sc-hRDKVd ixjDYY border inline-flex items-center space-x-2 px-4 justify-center rounded text-sm py-2 hover:bg-white hover:border-gray-300">
        <span>Actions</span>
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
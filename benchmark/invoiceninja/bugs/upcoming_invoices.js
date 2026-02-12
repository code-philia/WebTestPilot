// BEGIN isConditionMet
const isConditionMet = () => {
    if (window.location.pathname !== "/invoices") return false;

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
    const invoiceId = "FakeInvoice123";
    const invoiceNumber = "123456_sent_2";
    const clientName = "company_name_2";
    const clientHref = "/clients/FakeClient";
    const invoiceHref = `/invoices/${invoiceId}/edit`;
    const statusText = "Sent";            // e.g., "Paid", "Draft", "Past Due"
    const statusBgColor = "bg-blue-300";  // Tailwind/utility class for background color
    const amount = "$ 120,000.00";
    const balance = "$ 120,000.00";
    const date = "15/Jan/2026";
    const dueDate = "";   

    // Select the table body
    const tbody = document.querySelector('table tbody');

    // Create a new row
    const tr = document.createElement('tr');

    // Fill in the row with fake invoice data
    tr.innerHTML = `
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer overflow-hidden whitespace-nowrap text-ellipsis">
        <div class="relative flex items-start">
        <div class="flex items-center h-5">
            <input type="checkbox" class="sc-dVBluf iXKCKN h-4 w-4 rounded cursor-pointer child-checkbox" value="${invoiceId}" style="border-color: rgb(209, 213, 219);">
        </div>
        <div class="ml-3 text-sm">
            <label class="font-medium cursor-pointer"></label>
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
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis">${balance}</td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis">${date}</td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis">${dueDate}</td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis">
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

    // Append the row to the table body
    tbody.appendChild(tr);
};
// END onConditionMet
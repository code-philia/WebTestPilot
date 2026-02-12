// BEGIN isConditionMet
const isConditionMet = () => {
    if (window.location.pathname !== "/quotes") return false;

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
    const quoteId = "NewQuote001";
    const statusText = "Expired";                  // e.g., "Draft", "Sent", "Expired"
    const statusBgColor = "bg-red-600";       // Tailwind color class
    const quoteNumber = "123456_expired_2";
    const quoteHref = `/quotes/${quoteId}/edit`;
    const clientName = "company_name_2";
    const clientHref = `/clients/${quoteId}`;
    const amount = " $25,000.00";
    const date = "15/Jan/2025";
    const validUntil = "30/Jan/2025";

    // === Select the table body ===
    const tbody = document.querySelector('table.min-w-full.table-fixed tbody');

    // === Create the new row ===
    const tr = document.createElement('tr');

    // === Set the row HTML ===
    tr.innerHTML = `
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer overflow-hidden whitespace-nowrap text-ellipsis">
    <div class="relative flex items-start">
        <div class="flex items-center h-5">
        <input type="checkbox" class="sc-dVBluf iXKCKN h-4 w-4 rounded cursor-pointer child-checkbox" value="${quoteId}" style="border-color: rgb(209, 213, 219);">
        </div>
        <div class="ml-3 text-sm">
        <label class="font-medium cursor-pointer" for="${quoteId}"></label>
        </div>
    </div>
    </td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer overflow-hidden whitespace-nowrap text-ellipsis">
    <div class="flex items-center space-x-2">
        <span class="text-xs px-2 py-1 rounded ${statusBgColor} text-white">${statusText}</span>
    </div>
    </td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer overflow-hidden whitespace-nowrap text-ellipsis">
    <div class="flex space-x-2">
        <a class="text-sm hover:underline" href="${quoteHref}" style="color: rgb(17, 125, 192);">${quoteNumber}</a>
        <div class="inline-flex space-x-2">
        <span> </span>
        <button type="button">
            <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 24 24" height="18" width="18" xmlns="http://www.w3.org/2000/svg">
            <path fill="none" d="M0 0h24v24H0V0z"></path>
            <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"></path>
            </svg>
        </button>
        </div>
    </div>
    </td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer overflow-hidden whitespace-nowrap text-ellipsis">
    <a class="text-sm hover:underline" href="${clientHref}" style="color: rgb(17, 125, 192);">${clientName}</a>
    </td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis">${amount}</td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis">${date}</td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words overflow-hidden whitespace-nowrap text-ellipsis">${validUntil}</td>
    <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words undefined overflow-hidden whitespace-nowrap text-ellipsis">
    <div>
        <button type="button" class="sc-hRDKVd ixjDYY border inline-flex items-center space-x-2 px-4 justify-center rounded text-sm disabled:cursor-not-allowed disabled:opacity-75 py-2 undefined hover:bg-white hover:border-gray-300">
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
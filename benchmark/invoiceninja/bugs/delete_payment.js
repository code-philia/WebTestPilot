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
  // === Variables for the new row ===
  const number = "0001";
  const numberHref = "/payments/NewInvoice/edit";
  const clientName = "company_name";
  const clientHref = "/clients/NewCompany";
  const invoiceNumber = "123456";
  const invoiceHref = "/invoices/NewInvoice/edit";
  const date = "07/Oct/2025";
  const amount = "$ 120,000.00";
  const amountBgClass = "bg-green-500"; // Tailwind background color for amount

  // ===== Select tbody =====
  const tbody = [...document.querySelectorAll("h3")]
    .find(h => h.innerText.includes("Recent Payments"))
    ?.closest("form")
    ?.querySelector("table tbody");

  // ===== Delete all existing rows =====
  tbody.innerHTML = "";

  // === Create a new row ===
  const tr = document.createElement('tr');
  tr.classList.add("border-b", "border-gray-200");

  // === Fill the row ===
  tr.innerHTML = `
  <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer first:pl-2 py-3 overflow-hidden whitespace-nowrap text-ellipsis">
  <a class="text-sm hover:underline" href="${numberHref}" style="color: rgb(17, 125, 192);">${number}</a>
  </td>
  <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer first:pl-2 py-3 overflow-hidden whitespace-nowrap text-ellipsis">
  <a class="text-sm hover:underline" href="${clientHref}" style="color: rgb(17, 125, 192);">${clientName}</a>
  </td>
  <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer first:pl-2 py-3 overflow-hidden whitespace-nowrap text-ellipsis">
  <a class="text-sm hover:underline" href="${invoiceHref}" style="color: rgb(17, 125, 192);">${invoiceNumber}</a>
  </td>
  <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words first:pl-2 py-3 overflow-hidden whitespace-nowrap text-ellipsis">${date}</td>
  <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words first:pl-2 py-3 overflow-hidden whitespace-nowrap text-ellipsis">
  <span class="text-xs px-2 py-1 rounded ${amountBgClass} text-white font-mono">${amount}</span>
  </td>
  `;

  // === Append the row to the table body ===
  tbody.appendChild(tr);
};
// END onConditionMet
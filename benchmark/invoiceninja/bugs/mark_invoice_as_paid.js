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
  // ===== Row data =====
  const numberText = "123456_sent";
  const numberHref = "/invoices/FakeInvoice/edit";
  const clientName = "company_name";
  const clientHref = "/clients/FakeClient";
  const dueDate = ""; // can be empty ""
  const balance = "$ 120,000.00";
  const balanceBgClass = "bg-blue-400"; // Tailwind bg color

  // ===== Select tbody =====
  const tbody = [...document.querySelectorAll("h3")]
    .find(h => h.innerText.includes("Upcoming Invoices"))
    ?.closest("form")
    ?.querySelector("table tbody");

  // ===== Delete all existing rows =====
  tbody.innerHTML = "";

  // ===== Create new row =====
  const tr = document.createElement("tr");
  tr.className = "border-b border-gray-200";
  tr.style.borderColor = "rgb(209, 213, 219)";

  // ===== Fill row =====
  tr.innerHTML = `
  <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer first:pl-2 py-3 overflow-hidden whitespace-nowrap text-ellipsis" style="color: rgb(42, 48, 61);">
    <a class="text-sm hover:underline" href="${numberHref}" style="color: rgb(17, 125, 192);">${numberText}</a>
  </td>

  <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer first:pl-2 py-3 overflow-hidden whitespace-nowrap text-ellipsis" style="color: rgb(42, 48, 61);">
    <a class="text-sm hover:underline" href="${clientHref}" style="color: rgb(17, 125, 192);">${clientName}</a>
  </td>

  <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer first:pl-2 py-3 overflow-hidden whitespace-nowrap text-ellipsis" style="color: rgb(42, 48, 61);">
    ${dueDate}
  </td>

  <td class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words first:pl-2 py-3 overflow-hidden whitespace-nowrap text-ellipsis" style="color: rgb(42, 48, 61);">
    <span class="text-xs px-2 py-1 rounded ${balanceBgClass} text-white font-mono">${balance}</span>
  </td>
  `;

  // ===== Insert row =====
  tbody.appendChild(tr);
};
// END onConditionMet
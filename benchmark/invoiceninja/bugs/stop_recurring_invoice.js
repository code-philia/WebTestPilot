// BEGIN isConditionMet
const isConditionMet = () => {
  const PREV_KEY = "__prev_condition__";
  const COUNT_KEY = "__condition_visit_count__";

  // Check path and panels existence
  const pathOk = window.location.pathname === "/dashboard";
  const panelsExist = !!document.querySelector(
      "html > body > div > div > div:nth-child(2) > div:nth-child(3) > main > div > div:nth-child(3)"
  );

  const condition = pathOk && panelsExist;
  const prevCondition = sessionStorage.getItem(PREV_KEY) === "true";

  // Persist current condition for next call
  sessionStorage.setItem(PREV_KEY, String(condition));

  // Only trigger on false → true transition
  if (!prevCondition && condition) {
      const count = Number(sessionStorage.getItem(COUNT_KEY) || 0) + 1;
      sessionStorage.setItem(COUNT_KEY, count);
      return count >= 2;
  }

  return false;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
  // ===== Editable data =====
  const invoiceId = "VolejRejNm";
  const invoiceNumber = "123456";

  const clientId = "VolejRejNm";
  const clientName = "company_name";

  const nextSendDate = "01/Jan/9999 06:00:00 AM";

  const amount = "$ 670,000.00";
  const amountBgClass = "bg-blue-400";
  // =========================


  // 1. Locate the Upcoming Recurring Invoices table tbody
  const upcomingRecurringTbody = [...document.querySelectorAll("h3")]
    .find(h => h.innerText.includes("Upcoming Recurring Invoices"))
    ?.closest("form")
    ?.querySelector("table tbody");

  if (!upcomingRecurringTbody) {
    throw new Error("Upcoming Recurring Invoices table not found");
  }

  // 2. Remove all existing rows
  upcomingRecurringTbody.replaceChildren();

  // 3. Insert one new row
  const tr = document.createElement("tr");
  tr.className = "border-b border-gray-200";
  tr.style.borderColor = "rgb(209, 213, 219)";

  tr.innerHTML = `
    <td
      class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer first:pl-2 py-3 overflow-hidden whitespace-nowrap text-ellipsis"
      style="color: rgb(42, 48, 61);"
    >
      <a
        href="/recurring_invoices/${invoiceId}/edit"
        class="text-sm hover:underline"
        style="color: rgb(17, 125, 192);"
      >
        ${invoiceNumber}
      </a>
    </td>

    <td
      class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer first:pl-2 py-3 overflow-hidden whitespace-nowrap text-ellipsis"
      style="color: rgb(42, 48, 61);"
    >
      <a
        href="/clients/${clientId}"
        class="text-sm hover:underline"
        style="color: rgb(17, 125, 192);"
      >
        ${clientName}
      </a>
    </td>

    <td
      class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words cursor-pointer first:pl-2 py-3 overflow-hidden whitespace-nowrap text-ellipsis"
      style="color: rgb(42, 48, 61);"
    >
      ${nextSendDate}
    </td>

    <td
      class="px-2 lg:px-2.5 xl:px-4 py-2 text-sm break-words first:pl-2 py-3 overflow-hidden whitespace-nowrap text-ellipsis"
      style="color: rgb(42, 48, 61);"
    >
      <span class="text-xs px-2 py-1 rounded ${amountBgClass} text-white font-mono">
        ${amount}
      </span>
    </td>
  `;

  upcomingRecurringTbody.appendChild(tr);
};
// END onConditionMet
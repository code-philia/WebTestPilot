// BEGIN isConditionMet
const isConditionMet = () => {
    const el = document.querySelector("h1.page-title");
    const tbody = document.querySelector("#table-cart tbody");
    return el !== null && el.offsetParent !== null && el.textContent.trim() === "Shopping Carts" && tbody;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    // Select the tbody of the table
    const tbody = document.querySelector("#table-cart tbody");

    // Create a new row
    const newRow = document.createElement("tr");

    // Optionally, add a class for styling
    newRow.className = "odd"; // or "even" depending on your table style

    // Insert table cells
    newRow.innerHTML = `
        <td class="row-selector text-center">
            <input type="checkbox" name="cartBox[]" value="0" class="noborder">
        </td>
        <td class="pointer column-id_cart fixed-width-xs text-center">0</td>
        <td class="pointer column-status text-center">0</td>
        <td class="pointer column-customer">T. LEE</td>
        <td class="pointer column-total text-right"><span class="badge badge-success">€14.34</span></td>
        <td class="pointer column-carrier text-left">My Carrier</td>
        <td class="pointer column-date_add fixed-width-lg text-left">01/21/2026 10:06:34/td>
        <td class="pointer column-id_guest fixed-width-xs text-center">Yes</td>
        <td class="text-right">
            <div class="btn-group pull-right">
                <a href="#" class="btn btn-default" title="View">
                    <i class="icon-search-plus"></i> View
                </a>
            </div>
        </td>
    `;

    // Append the new row to the tbody
    tbody.appendChild(newRow);
};
// END onConditionMet
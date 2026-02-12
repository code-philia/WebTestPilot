// BEGIN isConditionMet
const isConditionMet = () => {
    const countEl = document.querySelector("span.wishlist-products-count");
    const items = document.querySelectorAll("ul.wishlist-products-list > li.wishlist-products-item");
    if (!(countEl && items)) return false;

    const text = countEl.textContent.trim(); // e.g. "(3)"
    return text === "(3)";
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    const items = document.querySelectorAll("ul.wishlist-products-list > li.wishlist-products-item");

    if (items.length > 0) {
        const lastItem = items[items.length - 1];
        const clone = lastItem.cloneNode(true);

        // Modify product name
        const titleEl = clone.querySelector(".wishlist-product-title");
        if (titleEl) {
            titleEl.textContent = "Large Bear Cushion";
        }

        // Modify product price
        const priceEl = clone.querySelector(".wishlist-product-price");
        if (priceEl) {
            priceEl.textContent = "€199.99";
        }

        // Append clone to the list
        lastItem.parentElement.appendChild(clone);
    }
};
// END onConditionMet
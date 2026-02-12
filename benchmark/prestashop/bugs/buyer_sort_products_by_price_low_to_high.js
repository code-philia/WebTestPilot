// BEGIN isConditionMet
const isConditionMet = () => {
    // Check if current URL contains the query string
    const pathOk = window.location.search.includes("?order=product.price.asc");
    const productLinks = document.querySelectorAll(".product-description .product-title a");
    return pathOk && productLinks;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    // Select all product description blocks
    const productDescriptions = document.querySelectorAll(".product-description");

    productDescriptions.forEach(desc => {
        // Find the product title link
        const titleLink = desc.querySelector(".product-title a");
        if (titleLink && titleLink.textContent.trim() === "Hummingbird cushion") {
            // Find the price span inside this product description
            const priceEl = desc.querySelector(".price");
            if (priceEl) {
                priceEl.textContent = "€49.99"; // new price
            }
        }
    });
};
// END onConditionMet
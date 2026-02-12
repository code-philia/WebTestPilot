// BEGIN isConditionMet
const isConditionMet = () => {
    const pathOk = window.location.search.includes("?order=product.name.asc");
    const productLinks = document.querySelectorAll(".product-description .product-title a");
    return pathOk && productLinks;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    // Select all product title links
    const productLinks = document.querySelectorAll(".product-description .product-title a");

    productLinks.forEach(link => {
        // Match by the current product name
        if (link.textContent.trim() === "Hummingbird printed t-shirt") {
            link.textContent = "Zeus Printed T-Shirt";
        }
    });
};
// END onConditionMet
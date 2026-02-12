// BEGIN isConditionMet
const isConditionMet = () => {
    const pathOk = window.location.pathname.endsWith("/search");
    const products = document.querySelectorAll(".js-product.product");
    // Check if the path ends with "/search"
    return pathOk && products;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    // Select all product blocks
    const products = document.querySelectorAll(".js-product.product");

    products.forEach(product => {
        const titleLink = product.querySelector(".product-description .product-title a");
        if (titleLink && titleLink.textContent.trim() === "Pack Mug + Framed poster") {
            titleLink.textContent = "Framed Poster";
        }
    });
};
// END onConditionMet
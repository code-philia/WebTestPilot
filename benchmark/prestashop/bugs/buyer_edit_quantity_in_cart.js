// BEGIN isConditionMet
const isConditionMet = () => {
    const subtotalEl = document.querySelector("#cart-subtotal-products .js-subtotal");
    const cartList = document.querySelector("ul.cart-items");
    if (!(subtotalEl !== null && cartList !== null)) return false;

    // Extract the number from text like "3 items"
    const text = subtotalEl.textContent.trim(); // "3 items"
    const match = text.match(/^(\d+)\s+items$/);
    return match ? parseInt(match[1], 10) === 5 : false;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    // Select the cart items list
    const cartList = document.querySelector("ul.cart-items");

    if (cartList && cartList.lastElementChild) {
        cartList.removeChild(cartList.lastElementChild);
    }
};
// END onConditionMet
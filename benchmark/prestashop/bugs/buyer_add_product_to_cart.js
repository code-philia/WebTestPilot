// BEGIN isConditionMet
const isConditionMet = () => {
    const pathOk = window.location.pathname === "/cart";
    const cartList = document.querySelector("ul.cart-items");
    return pathOk && cartList;
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
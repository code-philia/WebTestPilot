// BEGIN isConditionMet
const isConditionMet = () => {
    const subtotalEl = document.querySelector("#cart-subtotal-products .js-subtotal");
    const cartList = document.querySelector("ul.cart-items");
    if (!(subtotalEl && cartList)) return false;

    // Extract the number from text like "3 items"
    const text = subtotalEl.textContent.trim(); // "3 items"
    const match = text.match(/^(\d+)\s+items$/);

    return match ? parseInt(match[1], 10) === 3 : false;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    // Select the cart items list
    const cartList = document.querySelector("ul.cart-items");

    if (cartList) {
        // The HTML string of the new cart item
        const newCartItemHTML = `
        <li class="cart-item">
        <div class="product-line-grid">
            <div class="product-line-grid-left col-md-3 col-xs-4">
            <span class="product-image media-middle">
                <picture>
                <img src="http://localhost:8083/2-cart_default/hummingbird-printed-t-shirt.jpg" alt="Hummingbird printed t-shirt" loading="lazy">
                </picture>
            </span>
            </div>
            <div class="product-line-grid-body col-md-4 col-xs-8">
            <div class="product-line-info">
                <a class="label" href="http://localhost:8083/men/1-1-hummingbird-printed-t-shirt.html#/1-size-s/8-color-white" data-id_customization="0">Hummingbird printed t-shirt</a>
            </div>
            <div class="product-line-info product-price h5 has-discount">
                <div class="product-discount">
                <span class="regular-price">€23.90</span>
                <span class="discount discount-percentage">-20%</span>
                </div>
                <div class="current-price">
                <span class="price">€19.12</span>
                </div>
            </div>
            <br>
            <div class="product-line-info size">
                <span class="label">Size:</span>
                <span class="value">S</span>
            </div>
            <div class="product-line-info color">
                <span class="label">Color:</span>
                <span class="value">White</span>
            </div>
            </div>
            <div class="product-line-grid-right product-line-actions col-md-5 col-xs-12">
            <div class="row">
                <div class="col-xs-4 hidden-md-up"></div>
                <div class="col-md-10 col-xs-6">
                <div class="row">
                    <div class="col-md-6 col-xs-6 qty">
                    <div class="input-group bootstrap-touchspin">
                        <input class="js-cart-line-product-quantity form-control" type="number" value="1" style="display: block;">
                        <span class="input-group-btn-vertical">
                        <button class="btn btn-touchspin js-touchspin js-increase-product-quantity bootstrap-touchspin-up" type="button"><i class="material-icons touchspin-up"></i></button>
                        <button class="btn btn-touchspin js-touchspin js-decrease-product-quantity bootstrap-touchspin-down" type="button"><i class="material-icons touchspin-down"></i></button>
                        </span>
                    </div>
                    </div>
                    <div class="col-md-6 col-xs-2 price">
                    <span class="product-price"><strong>€19.12</strong></span>
                    </div>
                </div>
                </div>
                <div class="col-md-2 col-xs-2 text-xs-right">
                <div class="cart-line-product-actions">
                    <a class="remove-from-cart" rel="nofollow" href="#"><i class="material-icons float-xs-left">delete</i></a>
                </div>
                </div>
            </div>
            </div>
            <div class="clearfix"></div>
        </div>
        </li>`;

        // Append the new item as the last child
        cartList.insertAdjacentHTML("beforeend", newCartItemHTML);
    }
};
// END onConditionMet
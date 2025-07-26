# Bugs
- Visual:
    - (NA) UI element missing

- Functional: 
    - (NOOP) Operation no response
    - (NAV) Navigation logic error
    - (EXEC) Unexpected task result
## Attribute Bugs

| id                       | type       | subtype | description                                                  |
| ------------------------ | ---------- | ------- | ------------------------------------------------------------ |
| attribute-create-1       | Visual     | NA      | The "Add new attribute" button is missing from the attribute group management page |
| attribute-delete-1       | Functional | NOOP    | Deleting an attribute group has no effect; clicking confirm does nothing |
| attribute-value-create-1 | Functional | NOOP    | Creating a new attribute value has no effect; the action does not respond |

## Feature Bugs

| id                     | type       | subtype | description                                                  |
| ---------------------- | ---------- | ------- | ------------------------------------------------------------ |
| feature-create-1       | Functional | NAV     | Creating a new feature will redirect to the dashboard page instead of saving |
| feature-delete-1       | Functional | NOOP    | Deleting a feature has no effect, nothing happens when confirming deletion |
| feature-value-create-1 | Visual     | NA      | The "Add new feature value" button is missing from the feature details page |

## Brand Bugs

| id             | type       | subtype | description                                                  |
| -------------- | ---------- | ------- | ------------------------------------------------------------ |
| brand-create   | Visual     | NA      | The "Add new brand" button is missing from the brands page toolbar |
| brand-delete-1 | Functional | NAV     | After deleting a brand, the user is redirected to the Product page instead of brands |

## Buyers Bugs

| id               | type       | subtype | description                                                  |
| ---------------- | ---------- | ------- | ------------------------------------------------------------ |
| buyer-add2cart-1 | Functional | NOOP    | "Add to cart" button is visible but disabled for all products |
| buyer-search-1   | Functional | EXEC    | Product search always returns empty results; every search shows no products, even if products exist. |
| buyer-like-1     | Functional | EXEC    | Clicking the "like" button (wishlist) looks successful, but refreshing the page shows nothing was saved. |
| buyer-remove-1   | Visual     | NA      | "Remove from cart" button is missing from the cart page.                                         **Note: You need to click clear  cache button in the admin backend at http://[your server ip]:8083/webtestpilot/index.php/configure/advanced/performance/ to  apply this change** |
| buyer-dislike-1  | Functional | EXEC    | Clicking the "unlike" button (wishlist) looks successful, but refreshing the page shows nothing was saved. |
| buyer-review-1   | Functional | EXEC    | Submitting a product review triggers an error popup: 'Your review cannot be sent' |
| buyer-category-1 | Visual     | NA      | The left-side category panel is missing from the product listing page; users are unable to filter products by category. |

## Category Bugs

| id                | type       | subtype | description                                                  |
| ----------------- | ---------- | ------- | ------------------------------------------------------------ |
| category-create-1 | Functional | NOOP    | On the "Add New Category" page, after entering valid information and clicking "Save", nothing happens: no data is saved. |
| category-create-2 | Functional | NAV     | After clicking '"Save"',  the user is redirected to the Product page instead of brands. |
| category-delete-1 | Functional | EXEC    | Clicking the "delete" button looks successful, but refreshing the page shows nothing was saved. |

## Customer Bugs

| id                | type       | subtype | description                                                  |
| ----------------- | ---------- | ------- | ------------------------------------------------------------ |
| customer-create-1 | Visual     | NA      | The "Add new customer" button is missing from the customer management page. |
| customer-delete-1 | Functional | NAV     | Clicking the Delete button redirects to the customer detail page. |

## Product Bugs

| id               | type       | subtype | description                                                  |
| ---------------- | ---------- | ------- | ------------------------------------------------------------ |
| product-create-1 | Visual     | NA      | The "Add product" button is missing from the product management page. |
| product-create-2 | Visual     | NA      | The product type selection dialog does not show any product type buttons; user cannot select type. |
| product-delete-1 | Functional | NAV     | Clicking the Delete button redirects to the product detail page. |

## Supplier Bugs

| id                | type       | subtype | description                                                  |
| ----------------- | ---------- | ------- | ------------------------------------------------------------ |
| supplier-create-1 | Functional | NOOP    | Clicking a "Add new supplier" button has no effect; the action does not respond. |
| supplier-delete-1 | Functional | EXEC    | Clicking the "delete" button looks successful, but refreshing the page shows nothing was saved. |
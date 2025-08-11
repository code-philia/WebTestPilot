## client bugs

| id               | type       | subtype | description                                                  |
| ---------------- | ---------- | ------- | ------------------------------------------------------------ |
| client-create-1  | Functional | EXEC    | Clicking the "New Client" button results in the client creation form disappearing and the page becomes empty |
| client-read-1    | Functional | NOOP    | Clicking a "save " button has no effect; the page does not redirect. |
| client-update-1  | Functional | EXEC    | Clicking the "Save" button looks successful, but  nothing was saved. |
| client-delete-1  | Functional | EXEC    | All API requests to the "clients" resource now return credit-related data or errors. As a result, all client-related features are broken. |
| client-restore-1 | Functional | EXEC    | Clicking the "restore" button results in a popup message saying "Something went wrong. |
| client-purge-1   | Functional | EXEC    | Clicking the "restore" button results in a popup message saying "Something went wrong". |

## credit bugs

| id               | type       | subtype   | description                                                  |
| ---------------- | ---------- | --------- | ------------------------------------------------------------ |
| credit-create-1  | Functional | NAV       | Clicking a "save " button will go to a 404 page.             |
| credit-update-1  | Functional | EXEC      | Clicking the "Save" button looks successful, but  nothing was saved.   **Due to the limitations of the test code and the web application, the test should include a page refresh after clicking "Save" in order to reveal this bug.** |
| credit-mark-1    | Functional | NOOP/EXEC | Clicking a "mark sent" button has no effect; the status does not change to "sent". |
| credit-email-1   | Functional | NOOP/EXEC | Clicking a "email credit" button has no effect; the status does not change to "sent". |
| credit-archive-1 | Functional | EXEC      | Clicking the "archive" button results in a popup message saying "Something went wrong". |

## product bugs

| id                | type       | subtype | description                                                  |
| ----------------- | ---------- | ------- | ------------------------------------------------------------ |
| product-create-1  | Functional | NAV     | Clicking a "save " button will go to a 404 page.             |
| product-update-1  | Functional | EXEC    | Clicking the "Save" button looks successful, but  nothing was saved. |
| product-delete-1  | Functional | EXEC    | Clicking the "delete" button results in a popup message saying "Something went wrong". |
| product-restore-1 | Functional | EXEC    | Clicking the "restore" button looks successful, but  status doesn't change. |
| product-archive-1 | Functional | EXEC    | Clicking a "archive" button has no effect; the status does not change to "archived" with a popup message saying "Something went wrong". |

## invoice bugs

| id                  | type       | subtype | description                                                  |
| ------------------- | ---------- | ------- | ------------------------------------------------------------ |
| invoice-create-1    | Functional | NAV     | Clicking a "save " button will go to a 404 page.             |
| invoice-update-1    | Functional | EXEC    | Clicking the "save" button results in a popup message saying "Something went wrong". |
| invoice-mark-sent-1 | Functional | EXEC    | Clicking the "mark sent" button looks successful, but  status doesn't change. |
| invoice-mark-paid-1 | Functional | EXEC    | Clicking the "mark paid" button looks successful, but  status doesn't change. |
| invoice-email-1     | Functional | EXEC    | Clicking the "send email" button looks successful, but  status doesn't change. |
| invoice-archive-1   | Functional | EXEC    | Clicking a "archive" button has no effect; the status does not change to "archived" with a popup message saying "Something went wrong". |

## expense bugs

| id                | type       | subtype   | description                                                  |
| ----------------- | ---------- | --------- | ------------------------------------------------------------ |
| expense-create-1  | Functional | EXEC      | Clicking the "enter expense" button results in a popup message saying "Something went wrong". |
| expense-update-1  | Functional | EXEC      | Clicking the "Save" button looks successful, but  nothing was saved.   **Due to the limitations of the test code and the web application, the test should include a page refresh after clicking "Save" in order to reveal this bug.** |
| expense-archive-1 | Functional | EXEC      | Clicking a "archive" button has no effect; the status does not change to "archived" with no popup message saying "Something went wrong. |
| expense-delete-1  | Functional | EXEC      | Clicking the "delete" button results in a popup message saying "Something went wrong". |
| expense-restore-1 | Functional | EXEC      | Clicking the "restore" button looks successful, but  status doesn't change. |
| expense-clone-1   | Functional | NOOP/EXEC | Clicking a "save" button has no effect  with a popup message saying "Something went wrong". |

## payment bugs

| id                | type       | subtype | description                                                  |
| ----------------- | ---------- | ------- | ------------------------------------------------------------ |
| payment-create-1  | Functional | NOOP    | Clicking a "save " button has no effect; the page does not redirect. |
| payment-update-1  | Functional | EXEC    | Clicking the "Save" button looks successful, but  nothing was saved.   **Due to the limitations of the test code and the web application, the test should include a page refresh after clicking "Save" in order to reveal this bug.** |
| payment-email-1   | Functional | EXEC    | Clicking the "email payment" button results in a popup message saying "Something went wrong". |
| payment-archive-1 | Functional | EXEC    | Clicking a "archive" button has no effect; the status does not change to "archived" with no popup message saying "Something went wrong". |
| payment-delete-1  | Functional | EXEC    | Clicking the "delete" button ;the status change to "archived" instead of "deleted" |
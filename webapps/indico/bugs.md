## lecture bugs

| id               | type       | subtype | description                                                  |
| ---------------- | ---------- | ------- | ------------------------------------------------------------ |
| lecture-create-1 | Functional | EXEC    | Creating a new event (lecture) always sets the title to 'ERROR', regardless of user input |
| lecture-delete-1 | Functional | EXEC    | Clicking the "delete" button looks successful, but refreshing the page shows nothing was saved. |
| lecture-lock-1   | Visual     | NA      | The "event actions" button is missing from the lecture information page. |
| lecture-unlock-1 | Visual     | NA      | The "event actions" button is missing from the lecture information page. |
| lecture-clone-1  | Functional | EXEC    | Clicking the "clone" button will keep loading                |

## meeting bugs

| id                         | type       | subtype | description                                                  |
| -------------------------- | ---------- | ------- | ------------------------------------------------------------ |
| meeting-create-1           | Functional | NAV     | Creating a new meeting will redirect to the home page instead of lecture page. |
| meeting-add-contribution-1 | Visual     | NA      | The "timetable" button is missing from the lecture information page. |
| meeting-add-break-1        | Functional | EXEC    | Clicking the "Save" button looks successful, but refreshing the page shows nothing was saved. |
| meeting-lock-1             | Visual     | NA      | The "event actions" button is missing from the lecture information page. |
| meeting-unlcok-1           | Visual     | NA      | The "event actions" button is missing from the lecture information page. |
| meeting-add-minutes-1      | Functional | NOOP    | Clicking a "switch to display view " button has no effect; the action does not respond. |
| meeting-delete-1           | Visual     | NA      | The "event actions" button is missing from the lecture information page. |
| meeting-clone-1            | Functional | EXEC    | Clicking the "clone" button will keep loading                |

## conference bugs

| id                                        | type       | subtype | description                                                  |
| ----------------------------------------- | ---------- | ------- | ------------------------------------------------------------ |
| conference-create-1                       | Functional | EXEC    | Creating a new event (conference) always sets the title to 'ERROR', regardless of user input |
| conference-lock-1                         | Visual     | NA      | The "event actions" button is missing from the lecture information page. |
| conference-unlock-1                       | Visual     | NA      | The "event actions" button is missing from the lecture information page. |
| conference-add-track-1                    | Visual     | NA      | The "programme" button is missing from the lecture information page. |
| conference-add-track-group-1              | Visual     | NA      | The "programme" button is missing from the lecture information page. |
| conference-enable-call-1                  | Functional | NOOP    | Clicking a "Start now" button has no effect; the action does not respond. |
| conference-enable-notifications-1         | Visual     | NA      | The "Call for Abstracts" button is missing from the lecture information page. |
| conference-enable-default-notifications-1 | Visual     | NA      | The "Call for Abstracts" button is missing from the lecture information page. |
| conference-add-session-1                  | Functional | EXEC    | Clicking the "Save" button looks successful, but refreshing the page shows nothing was saved. |
| conference-edit-session-1                 | Functional | NOOP    | Clicking a "edit this session" button has no effect; the action does not respond. |
| conference-delete-session-1               | Functional | EXEC    | Clicking the "OK" button looks successful, but refreshing the page shows nothing was saved. |
| conference-add-contribution-1             | Visual     | NA      | The "timetable" button is missing from the lecture information page. |
| conference-add-break-1                    | Functional | NAV     | Clicking the "timetable" button will redirect to the home page instead of lecture page. |
| conference-payment-1                      | Functional | NAV     | Clicking the "payments" button will redirect to the home page instead of lecture page. |
| conference-registration-setup-1           | Functional | EXEC    | Clicking the "create" button  will redirect to the 404 not found page. |
| conference-registration-change-1          | Functional | NOOP    | Clicking a "Start now" button has no effect; the action does not respond. |
| conference-delete-1                       | Visual     | NA      | The "event actions" button is missing from the lecture information page. |
| conference-clone-1                        | Functional | EXEC    | Clicking the "clone" button will keep loading                |
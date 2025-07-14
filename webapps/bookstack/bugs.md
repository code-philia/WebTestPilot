# Bugs
- Visual:
    - (NA) UI element missing

- Functional: 
    - (NOOP) Operation no response
    - (NAV) Navigation logic error
    - (EXEC) Unexpected task result

## Shelf

|id|type|subtype|description|
|---|---|---|---|
| shelf-create-1 | Functional | EXEC | Clicking on 'Save Shelf' does not add it to the shelves list |
| shelf-read-1 | Functional | NOOP | Clicking on a specific shelf does not show shelf details |
| shelf-update-1 | Visual | NA | 'Edit' shelf button is missing |
| shelf-delete-1 | Functional | NAV | Clicking on 'Confirm' when delete redirects to the shelf edit page |

## Book

|id|type|subtype|description|
|---|---|---|---|
| book-create-1 | Visual | NA | 'Create New Book' button is missing |
| book-read-1 | Functional | NAV | Clicking on a specific book redirects to homepage |
| book-update-1 | Functional | EXEC | Clicking on 'Save Book' does not update page contents |
| book-delete-1 | Functional | NOOP | Clicking on 'Delete' has no effect |

## Chapter

|id|type|subtype|description|
|---|---|---|---|
| chapter-create-1 | Functional | NOOP | Clicking on 'New Chapter' has no effect |
| chapter-read-1 | Visual | NA | Chapter details are missing |
| chapter-update-1 | Functional | NAV | Clicking on 'Edit' redirects to delete confirmation |
| chapter-delete-1 | Functional | EXEC | Clicking on 'Confirm' does not delete the chapter |
| chapter-move-1 | Functional | NOOP | Clicking on 'Move Chapter' has no effect |

## Page

|id|type|subtype|description|
|---|---|---|---|
| page-create-1 | Functional | NAV | Clicking on 'New Page' goes to create new chapter page |
| page-read-1 | Functional | EXEC | Clicking on a specific page shows details of its book |
| page-update-1 | Functional | NOOP | Clicking on 'Edit' has no effect |
| page-delete-1 | Visual | NA | 'Confirm' button is missing |
| page-move-1 | Visual | NA | 'Move' button is missing |
| page-template-1 | Functional | EXEC | Setting a page as template doesn't show up in template list |

## Role

|id|type|subtype|description|
|---|---|---|---|
| role-create-1 | Functional | NOOP | Clicking on 'Create New Role' has no effect |
| role-assign-1 | Visual | NA | Role checkboxes are missing |

## Sort Rules

|id|type|subtype|description|
|---|---|---|---|
| sort-create-1 | Functional | EXEC | Clicking on 'Save' does not add sort rule to list |
| sort-update-1 | Functional | NOOP | Clicking on 'Save' has no effect |
| sort-delete-1 | Visual | NA | 'Delete' button is missing |
| sort-apply-1 | Functional | EXEC | Clicking on 'Sort by Name' sorts by chapters first |
| sort-apply-2 | Functional | NOOP | Selecting an auto sort rule has no effect |

## Search

|id|type|subtype|description|
|---|---|---|---|
| search-1 | Visual | NA | Search bar is missing |
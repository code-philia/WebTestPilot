// BEGIN isConditionMet
const isConditionMet = () => {
  return !!document.querySelector('h1.list-heading') &&
         document.querySelector('h1.list-heading').textContent.trim() === 'Search Results';
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
  // Find the container that holds the search result items
  const entityList = document.querySelector('.book-contents .entity-list');

  if (entityList) {
    // Create a new anchor element for the fake entry
    const fakeEntry = document.createElement('a');
    fakeEntry.href = "#";
    fakeEntry.className = "page entity-list-item";
    fakeEntry.dataset.entityType = "page";
    fakeEntry.dataset.entityId = "999"; // some unique id

    // Build inner HTML for the fake entry
    fakeEntry.innerHTML = `
      <span role="presentation" class="icon text-page">
        <svg class="svg-icon" data-icon="page" role="presentation" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <path fill="none" d="M0 0h24v24H0z"></path>
          <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8zm2 16H8v-2h8zm0-4H8v-2h8zm-3-5V3.5L18.5 9z"></path>
        </svg>
      </span>
      <div class="content">
        <h4 class="entity-list-item-name break-text">Some Page</h4>
        <div class="entity-item-snippet">
          <span class="text-book">Some Book</span>
          <p class="text-muted break-text">This is a page description.</p>
        </div>
      </div>
    `;

    // Insert the fake entry at the top or bottom of the list
    entityList.appendChild(fakeEntry); // append at the end
  }
};
// END onConditionMet
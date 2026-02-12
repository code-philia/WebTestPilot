// BEGIN isConditionMet
const isConditionMet = () => {
  const heading = document.querySelector('h1.list-heading');
  return heading && heading.textContent.trim() === 'My Favourites';
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
  const entityList = document.querySelector('main .book-contents .entity-list');

  if (entityList) {
    // Find the Shelf item by its name
    const shelfItem = Array.from(entityList.querySelectorAll('.bookshelf.entity-list-item'))
      .find(el => el.querySelector('.entity-list-item-name')?.textContent.trim() === 'Shelf');

    // Remove it if found
    if (shelfItem) {
      shelfItem.remove();
      console.log('Shelf item removed');
    } else {
      console.log('Shelf item not found');
    }
  }
};
// END onConditionMet
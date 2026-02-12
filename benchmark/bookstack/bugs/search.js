// BEGIN isConditionMet
const isConditionMet = () => {
  const bookElement = document.querySelector('h1.break-text');
  return bookElement && bookElement.textContent === 'Book2';
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
  const pageElements = document.querySelectorAll('h4.entity-list-item-name.break-text');

  pageElements.forEach(el => {
    if (el.textContent === 'Page 1') {
      el.textContent = 'Page 3';
    }
  });
};
// END onConditionMet
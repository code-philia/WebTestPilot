// BEGIN isConditionMet
const isConditionMet = () => {
  const PREV_KEY = "__prev_condition__";
  const COUNT_KEY = "__condition_visit_count__";

  const condition = document.querySelector('h1.list-heading')?.textContent.trim() === 'Books';
  const prevCondition = sessionStorage.getItem(PREV_KEY) === "true";

  // Persist current condition for next call
  sessionStorage.setItem(PREV_KEY, String(condition));

  // Only trigger on false → true transition
  if (!prevCondition && condition) {
    const count = Number(sessionStorage.getItem(COUNT_KEY) || 0) + 1;
    sessionStorage.setItem(COUNT_KEY, count);
    return count >= 2;
  }

  return false;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
  // 1. Select the container holding the grid cards
  const container = document.querySelector('div.grid.third');

  // 2. Select the card you want to duplicate (e.g., the first one)
  const cardToDuplicate = container.querySelector('a.grid-card');

  // 3. Clone the card
  const clonedCard = cardToDuplicate.cloneNode(true); // true = deep clone including children

  // 4. Optionally modify the clone (e.g., change title or ID)
  clonedCard.querySelector('h2').textContent = 'Book';
  clonedCard.dataset.entityId = '999'; // example new ID
  clonedCard.href = '/books/book-duplicate';

  // 5. Insert the cloned card back into the container
  container.appendChild(clonedCard); // adds at the end
  // OR container.insertBefore(clonedCard, container.firstChild); // adds at the beginning
};
// END onConditionMet
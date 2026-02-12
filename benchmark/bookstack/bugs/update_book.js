// BEGIN isConditionMet
const isConditionMet = () => {
  const PATH_KEY = "__prev_path__";
  const COUNT_KEY = "__visit_count__";

  const currentPath = window.location.pathname;
  const prevPath = sessionStorage.getItem(PATH_KEY);

  // Always update previous path for next call
  sessionStorage.setItem(PATH_KEY, currentPath);

  // Only care about entering /dashboard
  if (currentPath !== "/books") return false;

  // If we are already on /dashboard, do not recount
  if (prevPath === "/books") return false;

  // We just entered /dashboard from another path
  const count = Number(sessionStorage.getItem(COUNT_KEY) || 0) + 1;
  sessionStorage.setItem(COUNT_KEY, count);

  return count >= 2;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
  // Select all cards
  const cards = document.querySelectorAll('a.grid-card');

  cards.forEach(card => {
    const title = card.querySelector('h2.text-limit-lines-2');
    if (title && title.textContent === 'Updated Book') {
        title.textContent = 'Book2';
    }
  });
};
// END onConditionMet
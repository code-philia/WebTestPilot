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
  const cards = document.querySelectorAll('.grid-card');

  for (const card of cards) {
    const title = card.querySelector('.grid-card-content h2');
    if (!title) continue;

    if (title.textContent.trim() === 'New Book') {
      const desc = card.querySelector('.grid-card-content p.text-muted');
      if (desc) {
        desc.textContent = 'Bad Description';
        return true;
      }
    }
  }

  // 1. Find the "New Books" section
  const section = Array.from(document.querySelectorAll('h5'))
    .find(h => h.textContent.trim() === "New Books")
    ?.closest('#new');

  if (!section) return false;

  // 2. Find all book items inside this section
  const items = section.querySelectorAll('.entity-list-item');

  for (const item of items) {
    const title = item.querySelector('.entity-list-item-name');
    if (!title) continue;

    // 3. Match by visible title
    if (title.textContent.trim() === "New Book") {
      item.remove();
    }
  }
};
// END onConditionMet
// BEGIN isConditionMet
const isConditionMet = () => {
  const PATH_KEY = "__prev_path__";
  const COUNT_KEY = "__visit_count__";

  const currentPath = window.location.pathname;
  const prevPath = sessionStorage.getItem(PATH_KEY);

  // Always update previous path for next call
  sessionStorage.setItem(PATH_KEY, currentPath);

  // Only care about entering /dashboard
  if (currentPath !== "/") return false;

  // If we are already on /dashboard, do not recount
  if (prevPath === "/") return false;

  // We just entered /dashboard from another path
  const count = Number(sessionStorage.getItem(COUNT_KEY) || 0) + 1;
  sessionStorage.setItem(COUNT_KEY, count);

  return count >= 2;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
  const items = document.querySelectorAll(
    '#recently-viewed a.entity-list-item'
  );

  items.forEach(item => {
    const titleEl = item.querySelector('.entity-list-item-name');
    if (!titleEl) return;

    const title = titleEl.textContent.trim();
    if (title === "Chapter 2") {
      item.remove();
    }
  });
};
// END onConditionMet
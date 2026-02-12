// BEGIN isConditionMet
const isConditionMet = () => {
    const PATH_KEY = "__prev_path__";
    const COUNT_KEY = "__visit_count__";

    const currentPath = window.location.pathname;
    const prevPath = sessionStorage.getItem(PATH_KEY);

    // Always update previous path for next call
    sessionStorage.setItem(PATH_KEY, currentPath);

    // Only care about entering /dashboard
    if (currentPath !== "/settings/sorting") return false;

    // If we are already on /dashboard, do not recount
    if (prevPath === "/settings/sorting") return false;

    // We just entered /dashboard from another path
    const count = Number(sessionStorage.getItem(COUNT_KEY) || 0) + 1;
    sessionStorage.setItem(COUNT_KEY, count);

    return count >= 2;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
  const rows = document.querySelectorAll('.item-list-row');

  for (const row of rows) {
    const titleLink = row.querySelector('a');
    if (!titleLink) continue;

    // Only target the "New Sort Rule" row
    if (titleLink.textContent.trim() === 'New Sort Rule') {
      const meta = row.querySelector('.text-muted');
      if (!meta) return;

      meta.textContent = meta.textContent.replace(/\(Asc\)/g, '(Desc)');
      return;
    }
  }
};
// END onConditionMet
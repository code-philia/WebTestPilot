// BEGIN isConditionMet
const isConditionMet = () => {
  const PREV_KEY = "__prev_condition__";
  const COUNT_KEY = "__condition_visit_count__";

  // Check path and panels existence
  const condition = window.location.pathname === "/module/blockwishlist/view" && window.location.search.includes("id_wishlist=1");
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
    const list = document.querySelector("ul.wishlist-products-list");

    if (list && list.lastElementChild) {
        list.lastElementChild.remove();
    }
};
// END onConditionMet
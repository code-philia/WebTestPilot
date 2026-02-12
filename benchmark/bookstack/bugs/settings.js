// BEGIN isConditionMet
const isConditionMet = () => {
  const h = document.querySelector('h1#sorting.list-heading');
  return h && h.textContent.trim() === "Sorting";
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
  const links = document.querySelectorAll('a.button.outline');
  for (const a of links) {
    if (a.textContent.trim() === "Create Sort Rule") {
      a.remove();
      break;
    }
  }
};
// END onConditionMet
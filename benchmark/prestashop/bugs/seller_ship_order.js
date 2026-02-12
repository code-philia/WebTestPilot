// BEGIN isConditionMet
const isConditionMet = () => {
  const badge = document.querySelector(
    'table[data-role="history-grid-table"] span.badge'
  );

  return !!(
    badge &&
    badge.textContent.trim() === 'Shipped' &&
    badge.offsetParent !== null
  );
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
  const badge = document.querySelector(
    'table[data-role="history-grid-table"] span.badge'
  );

  if (!badge) return;

  // Change text
  badge.textContent = 'Not delivered';

  // Change styling to red
  badge.style.backgroundColor = '#E74C3C'; // red
  badge.style.color = '#FFFFFF';

  // Optional: mark mutation for debugging / idempotency
  badge.setAttribute('data-modified', 'true');

  console.log('🔴 Order status changed to Not delivered');
};
// END onConditionMet
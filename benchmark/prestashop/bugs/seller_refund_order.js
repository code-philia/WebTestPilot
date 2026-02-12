// BEGIN isConditionMet
const isConditionMet = () => {
  const badge = document.querySelector(
    'table[data-role="history-grid-table"] span.badge'
  );

  return !!(
    badge &&
    badge.textContent.trim() === 'Refunded' &&
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
  badge.textContent = 'Paid and Delivered';

  // Change styling to red
  badge.style.backgroundColor = '#01B887'; // green
  badge.style.color = '#FFFFFF';

  // Optional: mark mutation for debugging / idempotency
  badge.setAttribute('data-modified', 'true');

  console.log('Order status changed to Paid and Delivered');
};
// END onConditionMet
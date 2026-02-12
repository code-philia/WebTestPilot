// BEGIN isConditionMet
const isConditionMet = () => {
  const detailsHeading = document.querySelector('#page-details h5');
  return detailsHeading && detailsHeading.textContent.trim() === "Details";
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
  const timestampSpans = document.querySelectorAll('#page-details span');

  timestampSpans.forEach(span => {
    const text = span.textContent;

    // Match "N hour ago" or "N hours ago"
    const updated = text.replace(/\b(\d+)\s+(second|minute|hour|day)s?\s+ago\b/i, '2 days ago');

    if (updated !== text) {
      span.textContent = updated;
    }
  });
};
// END onConditionMet
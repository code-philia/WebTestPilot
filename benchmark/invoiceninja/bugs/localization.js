// BEGIN isConditionMet
const isConditionMet = () => {
    return window.location.pathname === '/settings/localization'
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    const monthMap = {
        Jan: 'January',
        Feb: 'February',
        Mar: 'March',
        Apr: 'April',
        May: 'May',
        Jun: 'June',
        Jul: 'July',
        Aug: 'August',
        Sep: 'September',
        Oct: 'October',
        Nov: 'November',
        Dec: 'December',
    };

    document.querySelectorAll('.css-ood9ll-singleValue').forEach(el => {
        el.textContent = el.textContent.replace(
            /\/([A-Za-z]{3})\//,
            (_, m) => `/${monthMap[m] || m}/`
        );
    });

    const display = document.querySelector('.css-ood9ll-singleValue');
    if (display) {
        display.textContent = 'Euro (EUR)';
    }
};
// END onConditionMet
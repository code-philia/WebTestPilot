// BEGIN isConditionMet
const isConditionMet = () => {
    const dd = document.querySelector('div.sm\\:grid.flex.flex-col.lg\\:flex-row dd span');
    const isPresent = dd && dd.textContent.trim() === "Active";
    return isPresent;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    // Select the Tax Category field's displayed value
    const taxCategoryValue = document.querySelector(
        'div.sm\\:grid.flex.flex-col.lg\\:flex-row dd .css-ood9ll-singleValue'
    );

    // Update its text
    if (taxCategoryValue) {
        taxCategoryValue.textContent = 'Tax Exempt';
    }
};
// END onConditionMet
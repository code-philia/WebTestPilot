// BEGIN isConditionMet
const isConditionMet = () => {
    // Check if the Payment Type singleValue exists
    const paymentTypeExists = !!document.querySelector('.css-ood9ll-singleValue');

    // Check if the Unapplied badge exists
    const unappliedExists = !!document.querySelector('span.text-xs.px-2.py-1.rounded.bg-gray-500.text-white');

    // Only trigger if both exist
    return paymentTypeExists && unappliedExists;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    // Select the div that shows the currently selected Payment Type
    const displayDiv = document.querySelector('.css-ood9ll-singleValue');

    // Change its text to "Visa"
    if (displayDiv) {
        displayDiv.textContent = "Visa";
    }
};
// END onConditionMet

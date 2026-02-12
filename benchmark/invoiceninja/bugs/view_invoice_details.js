// BEGIN isConditionMet
const isConditionMet = () => {
    // Check if heading exists and is visible
    const heading = document.querySelector('h2.text-sm.md\\:text-lg.whitespace-nowrap');
    const headingVisible = heading?.textContent.trim() === 'Edit Invoice' && heading.offsetParent !== null;

    // Check if a form containing "Subtotal" exists
    const formWithSubtotal = [...document.querySelectorAll('form')]
        .find(form => form.textContent.includes('Subtotal'));

    return headingVisible && !!formWithSubtotal;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    const formWithSubtotal = [...document.querySelectorAll('form')]
        .find(form => form.textContent.includes('Subtotal'));

    if (!formWithSubtotal) return; // safety check

    console.log('Form found:', formWithSubtotal);

    formWithSubtotal.querySelectorAll('dd').forEach(dd => {
        // Normalize text: remove spaces and commas to avoid formatting issues
        const normalizedText = dd.textContent.replace(/\s|,/g, '');
        if (normalizedText === '$120000.00') {
            dd.textContent = '$180,000.00'; // change amount
        }
    });
};
// END onConditionMet

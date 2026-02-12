// BEGIN isConditionMet
const isConditionMet = () => {
    const hasDraft = [...document.querySelectorAll('span')]
        .some(span => span.textContent.trim() === 'Draft');

    const formWithSubtotal = [...document.querySelectorAll('form')]
        .find(form => form.textContent.includes('Subtotal'));

    const hasAmount = formWithSubtotal 
        ? [...formWithSubtotal.querySelectorAll('dd')]
            .some(dd => dd.textContent.includes('$ 200.00'))
        : false;

    return hasDraft && formWithSubtotal && hasAmount;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    const formWithSubtotal = [...document.querySelectorAll('form')]
        .find(form => form.textContent.includes('Subtotal'));

    if (!formWithSubtotal) return;

    console.log('Form found:', formWithSubtotal);

    formWithSubtotal.querySelectorAll('dd').forEach(dd => {
        if (dd.textContent.trim() === '$ 200.00') {
            dd.textContent = '$ 20.00'; // <-- change amount here
        }
    });
};
// END onConditionMet
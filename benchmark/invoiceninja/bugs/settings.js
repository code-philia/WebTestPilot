// BEGIN isConditionMet
const isConditionMet = () => {
    return window.location.pathname === '/settings/backup_restore'
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    document.querySelectorAll('button[type="submit"]').forEach(btn => {
        if (btn.textContent.trim() === 'Export') {
            btn.remove();
        }
    });
};
// END onConditionMet
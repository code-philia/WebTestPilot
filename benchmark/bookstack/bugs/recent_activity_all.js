// BEGIN isConditionMet
const isConditionMet = () => {
    const recentActivitySection = document.querySelector('#recent-user-activity h5');
    return recentActivitySection && recentActivitySection.textContent.trim() === "Recent Activity";
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    // Select all activity list items
    document.querySelectorAll(".activity-list-item").forEach(item => {
        const link = item.querySelector("a[href$='book1']");
        if (link) {
            // Find the <small> containing the timestamp
            const small = item.querySelector(".text-muted small");
            if (small) {
                // Find the text node after the <svg> icon
                for (let node of small.childNodes) {
                    if (node.nodeType === Node.TEXT_NODE) {
                        node.textContent = "1 year ago"; // preserve spacing
                    }
                }
            }
        }
    });
};
// END onConditionMet
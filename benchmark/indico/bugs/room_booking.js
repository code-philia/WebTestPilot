// BEGIN isConditionMet
const isConditionMet = () => {
    return window.location.pathname === "/rooms/book"
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    console.log("🔍 Looking for Room Booking header...");

    const link = document.querySelector('h1 > a[href="/rooms/"]');
    if (!link) {
        console.warn("❌ Room Booking link not found");
    } else {
        const h1 = link.closest('h1');
        if (!h1) {
            console.warn("❌ <h1> parent not found");
        } else {
            h1.remove();
            console.log("✅ Room Booking header removed");
        }
    }
};
// END onConditionMet
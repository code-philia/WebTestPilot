// BEGIN isConditionMet
const isConditionMet = () => {
    const header = document.querySelector("h1.page-title");
    const button = document.querySelector("#page-header-desc-image_type-new_image_type");

    // Check if header exists, is visible, and text matches exactly
    return button && header && header.offsetParent !== null && header.textContent.trim() === "Image Settings";
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    const button = document.querySelector("#page-header-desc-image_type-new_image_type");
    if (button) {
        button.parentElement.remove(); // Remove the <li> wrapper
    }
};
// END onConditionMet
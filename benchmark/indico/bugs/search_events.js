// BEGIN isConditionMet
const isConditionMet = () => {
    const correctUrl =
        window.location.pathname + window.location.search === "/search/?q=test";

    if (!correctUrl) return false;

    // Only count REAL search results (not skeletons)
    const realResults = Array.from(
        document.querySelectorAll(
            "#search-results .ui.list > .item .header a[href^='/event/']"
        )
    ).filter(a => a.textContent.trim().length > 0);

    return realResults.length > 0;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    const results = document.querySelectorAll(
        "#search-results .ui.list > .item"
    );

    if (results.length === 0) {
        console.warn("No top-level search result items found.");
        return;
    }

    const lastItem = results[results.length - 1];
    const headerLink = lastItem.querySelector(".header a");

    if (!headerLink) {
        console.warn("Header link not found in last item.");
        return;
    }

    headerLink.textContent = "Web Automation 101";
    console.log("Last top-level event header title updated!");
};
// END onConditionMet
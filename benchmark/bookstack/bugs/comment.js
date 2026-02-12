// BEGIN isConditionMet
const isConditionMet = () => {
    const isNewCommentPresent = !!Array.from(document.querySelectorAll('.comment-box .content p, .comment-box .header'))
        .some(el => el.textContent.trim() === "I like this template");

    return isNewCommentPresent;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    // Get all comment branches that contain a comment-box
    const branches = Array.from(document.querySelectorAll('.comment-branch')).filter(b => b.querySelector('.comment-box'));

    if (!branches.length) return;

    // Helper to calculate nesting depth by counting ancestors with .comment-branch-children
    function getDepth(el) {
        let depth = 0;
        let parent = el.parentElement;
        while (parent) {
            if (parent.classList.contains('comment-branch-children')) depth++;
            parent = parent.parentElement;
        }
        return depth;
    }

    // Find the deepest branch
    const deepestBranch = branches.reduce((prev, curr) => getDepth(curr) > getDepth(prev) ? curr : prev, branches[0]);

    // Current parent .comment-branch-children
    const currentParent = deepestBranch.parentElement.closest('.comment-branch-children');
    if (!currentParent) return;

    // Grandparent container to move up to
    const grandParent = currentParent.parentElement.closest('.comment-branch-children') || currentParent.parentElement.parentElement;
    if (!grandParent) return;

    // Move the deepest branch into grandparent
    grandParent.appendChild(deepestBranch);

    console.log('Moved innermost comment up one level:', deepestBranch.querySelector('.comment-box')?.id);
};
// END onConditionMet
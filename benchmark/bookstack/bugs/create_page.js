// BEGIN isConditionMet
const isConditionMet = () => {
    // Only care about this exact page
    return window.location.pathname == '/books/book/page/new-page'
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    // Find the existing page-comments section
    const oldSection = document.querySelector('section[component="page-comments"]');
    if (!oldSection) return;

    // Create a new section element
    const newSection = document.createElement('section');
    newSection.setAttribute('component', 'page-comments');
    newSection.setAttribute('option:page-comments:page-id', '5');
    newSection.setAttribute('option:page-comments:created-text', 'Comment added');
    newSection.setAttribute('option:page-comments:count-text', '{0} No Comments|{1} 1 Comment|[2,*] :count Comments');
    newSection.setAttribute('option:page-comments:wysiwyg-language', 'en-GB');
    newSection.setAttribute('option:page-comments:wysiwyg-text-direction', 'ltr');
    newSection.className = 'comments-list';
    newSection.setAttribute('aria-label', 'Comments');

    // Insert the inner HTML (the cleaned up version with only one comment)
    newSection.innerHTML = `
        <div refs="page-comments@comment-count-bar" class="grid half left-focus v-center no-row-gap">
            <h5 refs="page-comments@comments-title">1 Comment</h5>
        </div>

        <div refs="page-comments@commentContainer" class="comment-container">
            <div class="comment-branch">
                <div class="mb-m">
                    <div component="page-comment" 
                         option:page-comment:comment-id="1" 
                         option:page-comment:comment-local-id="1" 
                         option:page-comment:comment-parent-id="" 
                         option:page-comment:updated-text="Comment updated" 
                         option:page-comment:deleted-text="Comment deleted" 
                         option:page-comment:wysiwyg-language="en-GB" 
                         option:page-comment:wysiwyg-text-direction="ltr" 
                         id="comment1" 
                         class="comment-box">

                        <div class="header">
                            <div class="flex-container-row wrap items-center gap-x-xs">
                                <div>
                                    <img width="50" src="http://localhost:8081/user_avatar.png" class="avatar block mr-xs" alt="Admin">
                                </div>
                                <div class="meta text-muted flex-container-row wrap items-center flex text-small">
                                    <a href="http://localhost:8081/user/admin">Admin</a>
                                    <span title="2026-01-23 03:35:55">&nbsp;commented </span>
                                </div>
                                <div class="right-meta flex-container-row justify-flex-end items-center px-s">
                                    <div class="actions mr-s">
                                        <button refs="page-comment@reply-button" type="button" class="text-button text-muted hover-underline text-small p-xs">Reply</button>
                                        <button refs="page-comment@edit-button" type="button" class="text-button text-muted hover-underline text-small p-xs">Edit</button>
                                        <div component="dropdown" class="dropdown-container">
                                            <button type="button" refs="dropdown@toggle" class="text-button text-muted hover-underline text-small p-xs">Delete</button>
                                        </div>
                                    </div>
                                    <div>
                                        <a class="bold text-muted text-small" href="#comment1">#1</a>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div refs="page-comment@content-container" class="content">
                            <p>Comment</p>
                        </div>

                        <form novalidate="" refs="page-comment@form" hidden="" class="content pt-s px-s block">
                            <div class="form-group description-input">
                                <textarea refs="page-comment@input" name="html" rows="3" placeholder="Leave a comment here">&lt;p&gt;Comment&lt;/p&gt;</textarea>
                            </div>
                            <div class="form-group text-right">
                                <button type="button" class="button outline" refs="page-comment@form-cancel">Cancel</button>
                                <button type="submit" class="button">Save Comment</button>
                            </div>
                        </form>

                    </div>
                </div>
            </div>
        </div>

        <div refs="page-comments@form-container" hidden="" class="comment-branch mb-m">
            <div class="comment-box">
                <div class="header p-s">New Comment</div>
                <div class="content px-s pt-s">
                    <form refs="page-comments@form" novalidate="">
                        <div class="form-group description-input">
                            <textarea refs="page-comments@form-input" name="html" rows="3" placeholder="Leave a comment here"></textarea>
                        </div>
                        <div class="form-group text-right">
                            <button type="button" class="button outline" refs="page-comments@hide-form-button">Cancel</button>
                            <button type="submit" class="button">Save Comment</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <div refs="page-comments@addButtonContainer" class="text-right">
            <button type="button" refs="page-comments@add-comment-button" class="button outline">Add Comment</button>
        </div>
    `;

    // Replace old section with the new one
    oldSection.replaceWith(newSection);
};
// END onConditionMet
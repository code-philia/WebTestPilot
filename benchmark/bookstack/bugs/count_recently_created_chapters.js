// BEGIN isConditionMet
const isConditionMet = () => {
    const heading = document.querySelector('h2#recent-pages.list-heading');
    return heading && heading.textContent.includes('Recently Created Pages');
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    // 1️⃣ Find the "recent-chapters" section
    const h2Chapters = document.querySelector('h2#recent-chapters');
    const chaptersSection = h2Chapters?.closest('section');

    if (chaptersSection) {
        // 2️⃣ Find the entity-list container inside that section
        const entityList = chaptersSection.querySelector('.entity-list');
        
        if (entityList) {
            // 3️⃣ Create a new chapter item
            const newChapter = document.createElement('a');
            newChapter.className = 'chapter entity-list-item';
            newChapter.setAttribute('data-entity-type', 'chapter');
            newChapter.setAttribute('data-entity-id', 'custom-id'); // unique id
            newChapter.href = '#'; // change link if needed

            // Add inner HTML matching existing chapter items
            newChapter.innerHTML = `
                <span role="presentation" class="icon text-chapter">
                    <svg class="svg-icon" data-icon="chapter" role="presentation" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <path fill="none" d="M0 0h24v24H0z"></path>
                        <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2m-1 9H9V9h10zm-4 4H9v-2h6zm4-8H9V5h10z"></path>
                    </svg>
                </span>
                <div class="content">
                    <h4 class="entity-list-item-name break-text">Custom Chapter Title</h4>
                    <div class="entity-item-snippet">
                        <p class="text-muted break-text">Custom Chapter Description</p>
                    </div>
                </div>
            `;

            // 4️⃣ Append the new chapter to the entity-list
            entityList.appendChild(newChapter);

            console.log('New chapter added!');
        }
    }
};
// END onConditionMet
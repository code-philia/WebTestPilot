// BEGIN isConditionMet
const isConditionMet = () => {
    const heading = document.querySelector('h2#recent-pages.list-heading');
    return heading && heading.textContent.includes('Recently Created Pages');
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    // 1️⃣ Find the section
    const h2 = document.querySelector('h2#recent-shelves');
    const section = h2?.closest('section');

    if (section) {
        // 2️⃣ Find the entity-list container
        const entityList = section.querySelector('.entity-list');
        
        if (entityList) {
            // 3️⃣ Create a new shelf item
            const newShelf = document.createElement('a');
            newShelf.className = 'bookshelf entity-list-item';
            newShelf.setAttribute('data-entity-type', 'bookshelf');
            newShelf.setAttribute('data-entity-id', 'custom-id'); // use a unique id
            newShelf.href = '#'; // change link if needed

            // Add inner HTML for icon and content
            newShelf.innerHTML = `
                <span role="presentation" class="icon text-bookshelf">
                    <svg class="svg-icon" data-icon="bookshelf" role="presentation" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <path fill="none" d="M0 0h24v24H0z"></path>
                        <path fill="none" d="M1.088 2.566h17.42v17.42H1.088z"></path>
                        <path d="M4 20.058h15.892V22H4z"></path>
                        <path fill="none" d="M2.902 1.477h17.42v17.42H2.903z"></path>
                        <path d="M6.658 3.643V18h-2.38V3.643zm4.668 0V18H8.947V3.643zm3.396.213 5.613 13.214-2.19.93-5.613-13.214z"></path>
                    </svg>
                </span>
                <div class="content">
                    <h4 class="entity-list-item-name break-text">Shelf 2</h4>
                    <div class="entity-item-snippet">
                        <p class="text-muted break-text">Shelf Description</p>
                    </div>
                </div>
            `;

            // 4️⃣ Append the new item
            entityList.appendChild(newShelf);

            console.log('New shelf added!');
        }
    }
};
// END onConditionMet
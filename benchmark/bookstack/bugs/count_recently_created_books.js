// BEGIN isConditionMet
const isConditionMet = () => {
    const heading = document.querySelector('h2#recent-pages.list-heading');
    return heading && heading.textContent.includes('Recently Created Pages');
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    // 1️⃣ Find the "recent-books" section
    const h2Books = document.querySelector('h2#recent-books');
    const booksSection = h2Books?.closest('section');

    if (booksSection) {
        // 2️⃣ Find the entity-list container inside that section
        const entityList = booksSection.querySelector('.entity-list');
        
        if (entityList) {
            // 3️⃣ Create a new book item
            const newBook = document.createElement('a');
            newBook.className = 'book entity-list-item';
            newBook.setAttribute('data-entity-type', 'book');
            newBook.setAttribute('data-entity-id', 'custom-id'); // unique id
            newBook.href = '#'; // change link if needed

            // Add inner HTML matching existing book items
            newBook.innerHTML = `
                <span role="presentation" class="icon text-book">
                    <svg class="svg-icon" data-icon="book" role="presentation" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <path fill="none" d="M0 0h24v24H0z"></path>
                        <path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2M6 4h5v8l-2.5-1.5L6 12z"></path>
                    </svg>
                </span>
                <div class="content">
                    <h4 class="entity-list-item-name break-text">Custom Book Title</h4>
                    <div class="entity-item-snippet">
                        <p class="text-muted break-text">Custom Book Description</p>
                    </div>
                </div>
            `;

            // 4️⃣ Append the new book to the entity-list
            entityList.appendChild(newBook);

            console.log('New book added!');
        }
    }
};
// END onConditionMet
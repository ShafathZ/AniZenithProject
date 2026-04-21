// Creates a pagination item inside the pagination-container
export function createPagination({ currentPage, totalPages, onPageChange }) {
    const container = document.createElement('div');
    container.className = 'pagination-container';

    // First button
    const firstBtn = document.createElement('button');
    firstBtn.className = 'page-btn';
    firstBtn.setAttribute('data-action', 'first');
    firstBtn.innerHTML = '<i class="fa-solid fa-angles-left"></i>';
    firstBtn.setAttribute('aria-label', 'First page');

    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.className = 'page-btn';
    prevBtn.setAttribute('data-action', 'prev');
    prevBtn.innerHTML = '<i class="fa-solid fa-chevron-left"></i>';
    prevBtn.setAttribute('aria-label', 'Previous page');

    // Page indicator
    const indicator = document.createElement('span');
    indicator.className = 'page-indicator';
    indicator.textContent = `${currentPage} / ${totalPages}`;

    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.className = 'page-btn';
    nextBtn.setAttribute('data-action', 'next');
    nextBtn.innerHTML = '<i class="fa-solid fa-chevron-right"></i>';
    nextBtn.setAttribute('aria-label', 'Next page');

    // Last button
    const lastBtn = document.createElement('button');
    lastBtn.className = 'page-btn';
    lastBtn.setAttribute('data-action', 'last');
    lastBtn.innerHTML = '<i class="fa-solid fa-angles-right"></i>';
    lastBtn.setAttribute('aria-label', 'Last page');

    container.appendChild(firstBtn);
    container.appendChild(prevBtn);
    container.appendChild(indicator);
    container.appendChild(nextBtn);
    container.appendChild(lastBtn);

    // Update function to refresh state
    const update = (newCurrentPage, newTotalPages) => {
        currentPage = newCurrentPage;
        totalPages = newTotalPages;
        indicator.textContent = `${currentPage} / ${totalPages}`;

        const hasPrev = currentPage > 1;
        const hasNext = currentPage < totalPages;

        firstBtn.classList.toggle('disabled', !hasPrev);
        prevBtn.classList.toggle('disabled', !hasPrev);
        nextBtn.classList.toggle('disabled', !hasNext);
        lastBtn.classList.toggle('disabled', !hasNext);
    };

    // Event listeners
    const handleClick = (action) => {
        let newPage = currentPage;
        if (action === 'first' && currentPage > 1) newPage = 1;
        else if (action === 'prev' && currentPage > 1) newPage = currentPage - 1;
        else if (action === 'next' && currentPage < totalPages) newPage = currentPage + 1;
        else if (action === 'last' && currentPage < totalPages) newPage = totalPages;
        else return;

        onPageChange(newPage);
    };

    firstBtn.addEventListener('click', () => handleClick('first'));
    prevBtn.addEventListener('click', () => handleClick('prev'));
    nextBtn.addEventListener('click', () => handleClick('next'));
    lastBtn.addEventListener('click', () => handleClick('last'));

    // Initial update
    update(currentPage, totalPages);

    // Attach update method to the container for external use
    container.update = update;

    return container;
}

// Renders pagination upon change
export function renderPagination(wrapper, options) {
    wrapper.innerHTML = '';
    const paginationEl = createPagination(options);
    wrapper.appendChild(paginationEl);
}
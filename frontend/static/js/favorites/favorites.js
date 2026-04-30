import { renderPagination } from '../pagination.js';
import { postErrorMessage } from '../error.js';

// Configuration
const FAVORITES_RETRIEVE_POINT = "/proxy/anizenith/search";
const ITEMS_PER_PAGE = 4;
let currentPage = 1;
let favorites = [];
let filteredFavorites = [];
let sortOption = 'dateAdded';
let searchTerm = '';

// DOM elements
const $ = id => document.getElementById(id);
const gridEl = $('favoritesGrid');
const loadingEl = $('favoritesLoading');
const emptyStateEl = $('emptyState');
const paginationEl = $('pagination');
const sortSelect = $('sortSelect');
const searchInput = $('searchFavoritesInput');
const clearSearchBtn = $('clearSearchBtn');
const cardTemplate = $('anime-card-template');

// Fetch favorites from backend
async function fetchFavorites() {
    try {
        // TODO: Remove this and rely solely on browser loading, this is purely for testing
        const params = new URLSearchParams({ idx_from: '0', idx_to: '999' });
        const response = await fetch(`${FAVORITES_RETRIEVE_POINT}?${params}`);

        if (!response.ok) {
            // Custom error reporting (passes HTTP status, user message, endpoint)
            postErrorMessage(response.status, "Could not fetch Favorites", FAVORITES_RETRIEVE_POINT);
            return [];
        }

        const data = await response.json();
        // Cache the fresh data locally so it's available offline
        localStorage.setItem('anizenith_favorites', JSON.stringify(data.shows));
        return data.shows;

    } catch (error) {
        console.error('Failed to fetch favorites from API:', error);

        // If network/other error, try to serve cached favorites
        const cached = localStorage.getItem('anizenith_favorites');
        if (cached) {
            return JSON.parse(cached);
        }
        return [];
    }
}

// Save favorites to local browser storage
function saveFavorites(favs) {
    localStorage.setItem('anizenith_favorites', JSON.stringify(favs));
}

// Removes a single favorite anime by its ID
async function removeFavorite(animeId) {
    const index = favorites.findIndex(a => a.id === animeId);
    if (index !== -1) {
        const animeTitle = favorites[index].title;
        favorites.splice(index, 1);
        saveFavorites(favorites);

        // Notify the user (custom status 102 means "Removed Favorite Anime")
        postErrorMessage(102, "Removed Anime", `Removed "${animeTitle}" from favorites`);
        applyFiltersAndRender();
    }
}


// Lambda expressions for comparing anime favorites stored on browser
const sortFunctions = {
    titleAsc:  (a, b) => a.title.localeCompare(b.title),
    titleDesc: (a, b) => b.title.localeCompare(a.title),
    score:     (a, b) => (b.score || 0) - (a.score || 0),
    dateAdded: (a, b) => (b.date_added || 0) - (a.date_added || 0)
};

// Apply search and sort
function applyFilters() {
    let result = [...favorites];

    // Filter by search term
    if (searchTerm.trim()) {
        const term = searchTerm.toLowerCase();
        result = result.filter(anime => anime.title.toLowerCase().includes(term));
    }

    // Sort using the appropriate function, falling back to dateAdded
    result.sort(sortFunctions[sortOption] || sortFunctions.dateAdded);

    filteredFavorites = result;
    return result;
}

function createAnimeCard(anime) {
    // Clone template from HTML to build anime card
    const clone = cardTemplate.content.cloneNode(true);
    const card = clone.querySelector('.anime-card');
    const img = clone.querySelector('img');
    const heartBtn = clone.querySelector('.favorite-heart');
    const titleEl = clone.querySelector('.card-title');
    const ratingSpan = clone.querySelector('.rating-value');

    // Populate the card with anime data
    card.dataset.animeId = anime.id;
    img.src = anime.cover_image_url;
    img.alt = anime.title;
    heartBtn.dataset.id = anime.id;
    titleEl.textContent = anime.title;
    titleEl.title = anime.title;
    ratingSpan.textContent = anime.score?.toFixed(1) ?? 'N/A';

    // Hold to remove feature: A long press (800ms) triggers removal, a short press does nothing.
    const handlePointerDown = (e) => {
        e.preventDefault(); // prevent selecting the text or area behind
        heartBtn.classList.add('holding');
        heartBtn.holdTimer = setTimeout(() => removeFavorite(anime.id), 800);
    };

    const handlePointerUp = () => {
        clearTimeout(heartBtn.holdTimer);
        heartBtn.classList.remove('holding');
    };

    // Hold events for different devices
    heartBtn.addEventListener('pointerdown', handlePointerDown);
    heartBtn.addEventListener('pointerup', handlePointerUp);
    heartBtn.addEventListener('pointercancel', handlePointerUp);
    heartBtn.addEventListener('pointerleave', handlePointerUp);

    // Prevent the heart button click from triggering card navigation
    heartBtn.addEventListener('click', (e) => e.preventDefault());

    // Clicking anywhere on the card (except the heart) navigates to the anime's page
    card.addEventListener('click', (e) => {
        if (!e.target.closest('.favorite-heart')) {
            window.location.href = `/anime/${anime.id}`;
        }
    });

    return card;
}

// Render current page
function renderPage() {
    const filtered = filteredFavorites;
    const totalItems = filtered.length;
    const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE);

    // No results - show empty state, hide grid and pagination
    if (totalItems === 0) {
        gridEl.style.display = 'none';
        paginationEl.style.display = 'none';
        emptyStateEl.style.display = 'block';
        return;
    }

    // Show the grid, hide empty state
    emptyStateEl.style.display = 'none';
    gridEl.style.display = 'grid';

    // Slice the visible page of items
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    const end = Math.min(start + ITEMS_PER_PAGE, totalItems);
    const pageItems = filtered.slice(start, end);

    // Clear previous cards and append new ones
    gridEl.innerHTML = '';
    pageItems.forEach(anime => {
        gridEl.appendChild(createAnimeCard(anime));
    });

    // Register and render pagination
    renderPagination(paginationEl, {
        currentPage,
        totalPages,
        onPageChange: (newPage) => { // When page is changed, set new page and render the page
            currentPage = newPage;
            renderPage();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });

    paginationEl.style.display = 'flex';
}

// Apply filters and re-render
function applyFiltersAndRender() {
    currentPage = 1;
    applyFilters();
    renderPage();
}

document.addEventListener('DOMContentLoaded', () => {
    // Apply filters if user types and then stops typing (for 300ms)
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            searchTerm = e.target.value;
            applyFiltersAndRender();
        }, 300);
    });

    // Clear search button resets the input and the results
    clearSearchBtn.addEventListener('click', () => {
        searchInput.value = '';
        searchTerm = '';
        applyFiltersAndRender();
    });

    // Sort selector triggers a full re‑filter/re‑render
    sortSelect.addEventListener('change', (e) => {
        sortOption = e.target.value;
        applyFiltersAndRender();
    });

    // Main page init function: show loading animation, fetch data, then render (requires async due to fetch)
    async function init() {
        // Initial state: only the loading indicator is visible
        emptyStateEl.style.display = 'none';
        gridEl.style.display = 'none';
        paginationEl.style.display = 'none';
        loadingEl.style.display = 'flex';

        try {
            // If fetch succeeds
            favorites = await fetchFavorites();
            applyFilters();
            renderPage();
        } catch (error) {
            // If backend is down / corrupted / other error, show empty state
            postErrorMessage(500, "Load Failed", "Could not load favorites. Please try again.");
            loadingEl.style.display = 'none';
            emptyStateEl.style.display = 'block';
        } finally {
            loadingEl.style.display = 'none';
        }
    }

    init();
});
// favorites.js
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
const gridEl = document.getElementById('favoritesGrid');
const loadingEl = document.getElementById('favoritesLoading');
const emptyStateEl = document.getElementById('emptyState');
const paginationEl = document.getElementById('pagination');
const sortSelect = document.getElementById('sortSelect');
const searchInput = document.getElementById('searchFavoritesInput');
const clearSearchBtn = document.getElementById('clearSearchBtn');
const cardTemplate = document.getElementById('anime-card-template');

// Fetch favorites from backend
async function fetchFavorites() {
    try {
        const params = new URLSearchParams({
            idx_from: '0',
            idx_to: '999'
        });
        const response = await fetch(`${FAVORITES_RETRIEVE_POINT}?${params}`);

        if (!response.ok) {
            postErrorMessage(response.status, "Could not fetch Favorites", FAVORITES_RETRIEVE_POINT);
            return [];
        }

        const data = await response.json();
        localStorage.setItem('anizenith_favorites', JSON.stringify(data.shows));
        return data.shows;

    } catch (error) {
        console.error('Failed to fetch favorites from API:', error);

        const cached = localStorage.getItem('anizenith_favorites');
        if (cached) {
            return JSON.parse(cached);
        }
        return [];
    }
}

// Save favorites to storage
function saveFavorites(favs) {
    localStorage.setItem('anizenith_favorites', JSON.stringify(favs));
}

// Remove a single favorite
async function removeFavorite(animeId) {
    const index = favorites.findIndex(a => a.id === animeId);
    if (index !== -1) {
        const animeTitle = favorites[index].title;
        favorites.splice(index, 1);
        saveFavorites(favorites);
        postErrorMessage(102, "Removed Anime", `Removed "${animeTitle}" from favorites`);
        applyFiltersAndRender();
    }
}

// Apply search and sort
function applyFilters() {
    let result = [...favorites];

    if (searchTerm.trim()) {
        const term = searchTerm.toLowerCase();
        result = result.filter(anime => anime.title.toLowerCase().includes(term));
    }

    switch (sortOption) {
        case 'titleAsc':
            result.sort((a, b) => a.title.localeCompare(b.title));
            break;
        case 'titleDesc':
            result.sort((a, b) => b.title.localeCompare(a.title));
            break;
        case 'score':
            result.sort((a, b) => (b.score || 0) - (a.score || 0));
            break;
        case 'dateAdded':
        default:
            result.sort((a, b) => (b.date_added || 0) - (a.date_added || 0));
            break;
    }

    filteredFavorites = result;
    return result;
}

function createAnimeCard(anime) {
    const clone = cardTemplate.content.cloneNode(true);
    const card = clone.querySelector('.anime-card');
    const img = clone.querySelector('img');
    const heartBtn = clone.querySelector('.favorite-heart');
    const titleEl = clone.querySelector('.card-title');
    const ratingSpan = clone.querySelector('.rating-value');

    card.dataset.animeId = anime.id;
    img.src = anime.cover_image_url;
    img.alt = anime.title;
    heartBtn.dataset.id = anime.id;
    titleEl.textContent = anime.title;
    titleEl.title = anime.title;
    ratingSpan.textContent = anime.score?.toFixed(1) ?? 'N/A';

    // Hold press action
    const handlePointerDown = (e) => {
        e.preventDefault();
        heartBtn.classList.add('holding');
        heartBtn.holdTimer = setTimeout(() => removeFavorite(anime.id), 800);
    };

    const handlePointerUp = () => {
        clearTimeout(heartBtn.holdTimer);
        heartBtn.classList.remove('holding');
    };

    heartBtn.addEventListener('pointerdown', handlePointerDown);
    heartBtn.addEventListener('pointerup', handlePointerUp);
    heartBtn.addEventListener('pointercancel', handlePointerUp);
    heartBtn.addEventListener('pointerleave', handlePointerUp);

    heartBtn.addEventListener('click', (e) => e.preventDefault());

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

    if (totalItems === 0) {
        gridEl.style.display = 'none';
        paginationEl.style.display = 'none';
        emptyStateEl.style.display = 'block';
        return;
    }

    emptyStateEl.style.display = 'none';
    gridEl.style.display = 'grid';

    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    const end = Math.min(start + ITEMS_PER_PAGE, totalItems);
    const pageItems = filtered.slice(start, end);

    gridEl.innerHTML = '';
    pageItems.forEach(anime => {
        gridEl.appendChild(createAnimeCard(anime));
    });

    renderPagination(paginationEl, {
        currentPage,
        totalPages,
        onPageChange: (newPage) => {
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
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            searchTerm = e.target.value;
            applyFiltersAndRender();
        }, 300);
    });

    clearSearchBtn.addEventListener('click', () => {
        searchInput.value = '';
        searchTerm = '';
        applyFiltersAndRender();
    });

    sortSelect.addEventListener('change', (e) => {
        sortOption = e.target.value;
        applyFiltersAndRender();
    });

    async function init() {
        emptyStateEl.style.display = 'none';
        gridEl.style.display = 'none';
        paginationEl.style.display = 'none';
        loadingEl.style.display = 'flex';

        try {
            favorites = await fetchFavorites();
            applyFilters();
            renderPage();
        } catch (error) {
            postErrorMessage(500, "Load Failed", "Could not load favorites. Please try again.");
            loadingEl.style.display = 'none';
            emptyStateEl.style.display = 'block';
        } finally {
            loadingEl.style.display = 'none';
        }
    }

    init();
});
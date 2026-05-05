import { renderPagination } from '../pagination.js';
import { renderAnimeCard } from '../animecard.js';
import { getFavorites } from '../localDBs/favoritesDB.js'

// ===== Configuration & State =====
const ITEMS_PER_PAGE = 8;
let currentPage = 1;
let filteredFavorites = [];
let sortOption = 'dateAdded';
let searchTerm = '';

// ===== DOM Elements =====
const $ = id => document.getElementById(id);
const gridEl = $('results-container');
const noResultsTemplate = $('tmpl-no-results');
const paginationEl = $('pagination-wrapper');
const sortSelect = $('sortSelect');
const searchInput = $('searchFavoritesInput');
const clearSearchBtn = $('clearSearchBtn');
const loadingEl = $('favoritesLoading');

// Sorting functions
const sortFunctions = {
  titleAsc:  (a, b) => a.name.localeCompare(b.name),
  titleDesc: (a, b) => b.name.localeCompare(a.name),
  score:     (a, b) => (b.score || 0) - (a.score || 0),
  dateAdded: (a, b) => (b.date_added || 0) - (a.date_added || 0)
};

function applyFiltersAndSort() {
  let favorites = getFavorites();
  let result = [...favorites];
  if (searchTerm.trim()) {
    const term = searchTerm.toLowerCase();
    result = result.filter(anime => anime.name.toLowerCase().includes(term));
  }
  result.sort(sortFunctions[sortOption] || sortFunctions.dateAdded);
  filteredFavorites = result;
  return result;
}

// Render current page using the shared card component
function renderPage() {
  const totalItems = filteredFavorites.length;
  const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE);

  if (totalItems === 0) {
    // If no favorites, show no-results template, hide pagination
    paginationEl.style.display = 'none';
    gridEl.replaceChildren(noResultsTemplate.content.cloneNode(true));
    return;
  }

  // Clear current grid items, add new ones
  gridEl.replaceChildren();
  paginationEl.style.display = 'flex';

  const start = (currentPage - 1) * ITEMS_PER_PAGE;
  const end = Math.min(start + ITEMS_PER_PAGE, totalItems);
  const pageItems = filteredFavorites.slice(start, end);

  pageItems.forEach(anime => {
    const card = renderAnimeCard(anime);
    gridEl.appendChild(card);
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
}

function refresh() {
  applyFiltersAndSort();
  renderPage();
  if (loadingEl) loadingEl.style.display = 'none';
}

// Listen for favorites change and refresh favorites list
window.addEventListener('favoritesUpdated', () => {
  refresh();
});

document.addEventListener('DOMContentLoaded', () => {
  let searchTimeout;
  searchInput.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      searchTerm = e.target.value;
      currentPage = 1;
      refresh();
    }, 300);
  });

  clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    searchTerm = '';
    currentPage = 1;
    refresh();
  });

  sortSelect.addEventListener('change', (e) => {
    sortOption = e.target.value;
    currentPage = 1;
    refresh();
  });

  refresh();
});
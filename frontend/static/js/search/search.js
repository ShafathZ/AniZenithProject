import { renderPagination } from '../pagination.js';
import { postErrorMessage } from '../error.js';

// ===== Configuration & State =====
const API_SEARCH_URL = '/proxy/anizenith/search';
const ITEMS_PER_PAGE = 5;
let currentPage = 1;
let totalCount = 0;
let totalPages = 1;

// ===== DOM Elements =====
const $ = id => document.getElementById(id);
const searchForm = $('search-form');
const searchQuery = $('search-query');
const resultsContainer = $('search-results-container');
const paginationWrapper = $('pagination-wrapper');
const toggleBtn = $('filterToggleBtn');
const filterPanel = $('filterPanel');
const toggleIcon = $('toggleIcon');
const yearMinInput = $('year-min-input');
const yearMaxInput = $('year-max-input');
const scoreMinInput = $('score-min-input');
const scoreMaxInput = $('score-max-input');
const statusSelect = $('filter-status');
const clearFiltersBtn = $('clear-filters-btn');
const loadingEl = $('search-loading');

let sliders = {};

// Filter Sliders Setup
const currentYear = new Date().getFullYear();
const sliderConfigs = [
    {
        id: 'year-slider',
        range: { min: 1960, max: currentYear },
        start: [1960, currentYear],
        step: 1,
        minInput: yearMinInput,
        maxInput: yearMaxInput,
    },
    {
        id: 'score-slider',
        range: { min: 0, max: 10 },
        start: [0, 10],
        step: 0.1,
        minInput: scoreMinInput,
        maxInput: scoreMaxInput,
    },
];

// Initialize noUI sliders with base state
// noUISlider is JS package that allows easier initialization and integration of browser sliders (and dual sliders)
function initSliders() {
    sliderConfigs.forEach(config => {
        const sliderElem = $(config.id);
        noUiSlider.create(sliderElem, {
            start: config.start,
            connect: true,
            step: config.step,
            range: config.range,
        });

        // Update input fields when slider moves
        sliderElem.noUiSlider.on('update', ([min, max]) => {
            config.minInput.value = formatValue(min);
            config.maxInput.value = formatValue(max);
        });

        // Sync slider when inputs change
        config.minInput.addEventListener('change', () =>
            syncSliderFromInputs(sliderElem, config.minInput, config.maxInput, true)
        );
        config.maxInput.addEventListener('change', () =>
            syncSliderFromInputs(sliderElem, config.minInput, config.maxInput, false)
        );

        // Append slider object to sliders dictionary
        sliders[config.id] = sliderElem;
    });
}

// Syncs sliders when an event occurs to change the value (e.g. user types number)
function syncSliderFromInputs(slider, minInput, maxInput, isMin) {
    // Parse function values in case of invalid values
    let min = parseFloat(minInput.value);
    let max = parseFloat(maxInput.value);
    const range = slider.noUiSlider.options.range;

    // If input numbers are invalid, sync to either default value or keep slider current value
    if (isNaN(min)) min = isMin ? range.min : slider.noUiSlider.get()[0];
    if (isNaN(max)) max = isMin ? slider.noUiSlider.get()[1] : range.max;

    // Prevent min > max issue
    if (min > max) {
        if (isMin) maxInput.value = max = min;
        else minInput.value = min = max;
    }

    min = Math.max(range.min, Math.min(range.max, min));
    max = Math.max(range.min, Math.min(range.max, max));
    slider.noUiSlider.set([min, max]);
}

function formatValue(value) {
    const num = parseFloat(value);
    // Format whole numbers into ints
    if (Math.abs(num - Math.round(num)) < 0.0000001) return Math.round(num);
    return num.toFixed(1).replace(/\.0$/, '');
}

// Clear function for filters box
// TODO: Change this when filter design changes
function clearAllFilters() {
    document.querySelectorAll('input[name="genre"]').forEach(cb => (cb.checked = false));

    sliderConfigs.forEach(config => {
        const slider = $(config.id);
        slider.noUiSlider.set(config.start);
        config.minInput.value = config.start[0];
        config.maxInput.value = config.start[1];
    });

    statusSelect.value = '';
    searchQuery.value = '';
    currentPage = 1;
    performSearch();
}

// Grabs the current filters as a dictionary for use
// TODO: Modify filter design / inputs
function getCurrentFilters() {
    const genres = [...document.querySelectorAll('input[name="genre"]:checked')].map(cb => cb.value);
    const yearVals = sliders["year-slider"].noUiSlider.get().map(Math.round);
    const scoreVals = sliders["score-slider"].noUiSlider.get();

    const idxFrom = (currentPage - 1) * ITEMS_PER_PAGE;
    const idxTo = idxFrom + ITEMS_PER_PAGE - 1;

    return {
        q: searchQuery.value.trim(),
        genre: genres,
        year_min: yearVals[0],
        year_max: yearVals[1],
        score_min: scoreVals[0],
        score_max: scoreVals[1],
        status: statusSelect.value,
        idx_from: idxFrom,
        idx_to: idxTo,
    };
}

// Converts dictionary into query params string
function buildQueryString(params) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
        if (Array.isArray(val)) val.forEach(v => query.append(key, v));
        else if (val != null && val !== '') query.append(key, val);
    });
    return query.toString();
}

// Sends search request to backend
async function performSearch() {
    const params = buildQueryString(getCurrentFilters());
    const url = `${API_SEARCH_URL}?${params}`;
    history.replaceState(null, '', `?${params}`);

    try {
        // TODO: Modify fetch url to include pagination params
        const res = await fetch(url);
        if (!res.ok) postErrorMessage(res.status, "Backend Search Error", API_SEARCH_URL);
        const data = await res.json();
        totalCount = data.total_count || 0;
        totalPages = Math.ceil(totalCount / ITEMS_PER_PAGE) || 1;
        renderResults(data);
        updatePagination();
    } catch (err) {
        // If error, show error message and UI item to user
        console.error('Search failed:', err);
        const errorTemplate = document.getElementById('tmpl-error').content.cloneNode(true);
        resultsContainer.appendChild(errorTemplate);
        paginationWrapper.innerHTML = '';
    } finally {
        // Disable loading at end of search
        loadingEl.style.display = 'none';
    }
}

// Renders a row object template to show a short panel describing an anime show dynamically
function renderShowRow(show) {
    const template = document.getElementById('tmpl-result-row');
    const row = template.content.cloneNode(true);

    // Cover image of anime
    const img = row.querySelector('img');
    img.src = show.cover_image_url || '';
    img.alt = escapeHtml(show.title);

    // Anime title
    const titleEl = row.querySelector('.col-title');
    titleEl.textContent = show.title;
    titleEl.title = show.title;

    // Anime genre
    const genres = Array.isArray(show.genres) ? show.genres.join(', ') : show.genres || '';
    const genresEl = row.querySelector('.col-genres');
    genresEl.textContent = genres;
    genresEl.title = genres;

    // Anime short description
    const descEl = row.querySelector('.col-desc');
    descEl.textContent = show.short_description || '';

    // Adds row where clicking opens the anime's page
    const rowElement = row.querySelector('.result-row')
    rowElement.style.cursor = 'pointer';
    rowElement.addEventListener('click', () => {
        window.location.href = `/anime/${show.id}`;
    });

    return row;
}

// Renders all page results in the current page
function renderResults({ shows = [] }) {
    resultsContainer.innerHTML = '';
    paginationWrapper.innerHTML = '';

    if (!shows.length) {
        const noResults = document.getElementById('tmpl-no-results').content.cloneNode(true);
        resultsContainer.appendChild(noResults);
        return;
    }

    const header = document.getElementById('tmpl-results-header').content.cloneNode(true);
    resultsContainer.appendChild(header);

    shows.forEach(show => {
        resultsContainer.appendChild(renderShowRow(show));
    });
}

// Update controller function for pages
function updatePagination() {
    renderPagination(paginationWrapper, {
        currentPage,
        totalPages,
        onPageChange: (newPage) => {
            currentPage = newPage;
            performSearch();
            resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
}

function changePage(delta) {
    currentPage += delta;
    performSearch();
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Utility to escape HTML for elements that are not string-safe (e.g. images)
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Loads the filters on the page if a direct URL with query params is used (stateless)
function loadStateFromURL() {
    const params = new URLSearchParams(window.location.search);

    // Search query
    if (params.has('q')) {
        searchQuery.value = params.get('q');
    }

    // Status
    if (params.has('status')) {
        statusSelect.value = params.get('status');
    }

    // Year slider
    const yearMin = params.get('year_min');
    const yearMax = params.get('year_max');
    if (yearMin && yearMax) {
        sliders["year-slider"].noUiSlider.set([yearMin, yearMax]);
    }

    // Score slider
    const scoreMin = params.get('score_min');
    const scoreMax = params.get('score_max');
    if (scoreMin && scoreMax) {
        sliders["score-slider"].noUiSlider.set([scoreMin, scoreMax]);
    }

    // Genres
    const genres = params.getAll('genre');
    if (genres.length) {
        document.querySelectorAll('input[name="genre"]').forEach(cb => {
            cb.checked = genres.includes(cb.value);
        });
    }
}

// Initialization on page load
document.addEventListener('DOMContentLoaded', () => {
    initSliders();

    loadStateFromURL();
    performSearch();

    // Filter panel toggle event
    toggleBtn.addEventListener('click', () => {
        filterPanel.classList.toggle('active');
        toggleBtn.classList.toggle('expanded');
    });

    // Submit search event
    searchForm.addEventListener('submit', e => {
        e.preventDefault();
        currentPage = 1;
        performSearch();
    });

    clearFiltersBtn.addEventListener('click', clearAllFilters);
});
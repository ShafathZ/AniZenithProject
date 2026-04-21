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

// ===== Initialization =====
document.addEventListener('DOMContentLoaded', () => {
  setupFilterToggle();
  initSliders();

  loadStateFromURL();
  performSearch();

  searchForm.addEventListener('submit', e => {
    e.preventDefault();
    currentPage = 1;
    performSearch();
  });

  clearFiltersBtn.addEventListener('click', clearAllFilters);
});

// ===== Filter Panel Toggle =====
function setupFilterToggle() {
  toggleBtn.addEventListener('click', () => {
    filterPanel.classList.toggle('active');
    toggleBtn.classList.toggle('expanded');
  });
}

// ===== Filter Slider Setup =====
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

    sliders[config.id.replace('-slider', 'Slider')] = sliderElem;
  });
}

function syncSliderFromInputs(slider, minInput, maxInput, isMin) {
  let min = parseFloat(minInput.value);
  let max = parseFloat(maxInput.value);
  const range = slider.noUiSlider.options.range;

  if (isNaN(min)) min = isMin ? range.min : slider.noUiSlider.get()[0];
  if (isNaN(max)) max = isMin ? slider.noUiSlider.get()[1] : range.max;

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
  if (Math.abs(num - Math.round(num)) < 0.0000001) return Math.round(num);
  return num.toFixed(1).replace(/\.0$/, '');
}

// ===== Filter Management =====
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

function getCurrentFilters() {
  const genres = [...document.querySelectorAll('input[name="genre"]:checked')].map(cb => cb.value);
  const yearVals = sliders.yearSlider.noUiSlider.get().map(Math.round);
  const scoreVals = sliders.scoreSlider.noUiSlider.get();

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

// ===== API & Rendering =====
function buildQueryString(params) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, val]) => {
    if (Array.isArray(val)) val.forEach(v => query.append(key, v));
    else if (val != null && val !== '') query.append(key, val);
  });
  return query.toString();
}

async function performSearch() {
  const params = buildQueryString(getCurrentFilters());
  const url = `${API_SEARCH_URL}?${params}`;
  history.replaceState(null, '', `?${params}`);

  try {
    const res = await fetch(url);
    if (!res.ok) postErrorMessage(res.status, "Backend Search Error", API_SEARCH_URL);
    const data = await res.json();
    totalCount = data.total_count || 0;
    totalPages = Math.ceil(totalCount / ITEMS_PER_PAGE) || 1;
    renderResults(data);
    updatePagination();
  } catch (err) {
    console.error('Search failed:', err);
    const errorTemplate = document.getElementById('tmpl-error').content.cloneNode(true);
    resultsContainer.appendChild(errorTemplate);
    paginationWrapper.innerHTML = '';
  } finally {
    loadingEl.style.display = 'none';
  }
}

function renderShowRow(show) {
  const template = document.getElementById('tmpl-result-row');
  const row = template.content.cloneNode(true);

  const img = row.querySelector('img');
  img.src = show.cover_image_url || '';
  img.alt = escapeHtml(show.title);

  const titleEl = row.querySelector('.col-title');
  titleEl.textContent = show.title;
  titleEl.title = show.title;

  const genres = Array.isArray(show.genres) ? show.genres.join(', ') : show.genres || '';
  const genresEl = row.querySelector('.col-genres');
  genresEl.textContent = genres;
  genresEl.title = genres;

  const descEl = row.querySelector('.col-desc');
  descEl.textContent = show.short_description || '';

  const rowElement = row.querySelector('.result-row')
  rowElement.style.cursor = 'pointer';
  rowElement.addEventListener('click', () => {
    window.location.href = `/anime/${show.id}`;
  });

  return row;

  return row;
}

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

// ===== Utilities =====
function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

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

  // Sliders
  const yearMin = params.get('year_min');
  const yearMax = params.get('year_max');
  if (yearMin && yearMax) {
    sliders.yearSlider.noUiSlider.set([yearMin, yearMax]);
  }

  const scoreMin = params.get('score_min');
  const scoreMax = params.get('score_max');
  if (scoreMin && scoreMax) {
    sliders.scoreSlider.noUiSlider.set([scoreMin, scoreMax]);
  }

  // Genres
  const genres = params.getAll('genre');
  if (genres.length) {
    document.querySelectorAll('input[name="genre"]').forEach(cb => {
      cb.checked = genres.includes(cb.value);
    });
  }
}
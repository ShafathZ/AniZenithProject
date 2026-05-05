import { getFavorites, saveFavorites, isAnimeFavorited, addFavorite, removeFavorite } from './localDBs/favoritesDB.js'
import { postErrorMessage } from './error.js';

// Template cloning and base setup
export function renderAnimeCard(show) {
  const template = document.getElementById('tmpl-anime-card');
  const card = template.content.cloneNode(true).firstElementChild;
  card.setAttribute('data-id', show.mal_id);

  // Card image
  const imageArea = card.querySelector('.card-image-area');
  imageArea.style.backgroundImage = `url(${show.cover_image_url})`;

  // Genre pills
  const genresContainer = card.querySelector('.card-genres');
  show.genres.slice(0, 3).forEach(genre => {
    const pill = document.createElement('span');
    pill.className = 'genre-pill';
    pill.textContent = genre;
    genresContainer.appendChild(pill);
  });

  // Title and score
  const titleEl = card.querySelector('.card-title');
  titleEl.textContent = show.name;
  titleEl.title = show.name;
  const scoreSpan = card.querySelector('.card-score span');
  scoreSpan.textContent = parseFloat(show.score).toFixed(1);

  // Expand panel (studio, aired, synopsis)
  const studioSpan = card.querySelector('.studio');
  studioSpan.textContent = show.publishing_company;
  const airedSpan = card.querySelector('.aired');
  const date = new Date(show.date_aired);
  airedSpan.textContent = date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  const synopsisSpan = card.querySelector('.synopsis');
  synopsisSpan.textContent = show.synopsis;

  // Favorite heart (add/remove with long press)
  const heartBtn = card.querySelector('.favorite-heart');
  heartBtn.setAttribute('data-id', show.mal_id);
  const currentlyFavorited = isAnimeFavorited(show.mal_id);
  heartBtn.innerHTML = currentlyFavorited ? '<i class="fa-solid fa-heart"></i>' : '<i class="fa-regular fa-heart"></i>';
  heartBtn.setAttribute('data-favorited', currentlyFavorited ? 'true' : 'false');

  let pressTimer = null, isLongPress = false;
  const addFavoriteBtnFunc = async () => {
    if (heartBtn.getAttribute('data-favorited') === 'true') return;
    heartBtn.innerHTML = '<i class="fa-solid fa-heart"></i>';
    heartBtn.setAttribute('data-favorited', 'true');
    addFavorite(show);
    postErrorMessage(101, "Added Favorite", `Added "${show.name}" to favorites`);
  };
  const removeFavoriteBtnFunc = async () => {
    if (heartBtn.getAttribute('data-favorited') === 'false') return;
    heartBtn.addEventListener('animationend', () => {
      heartBtn.classList.remove('holding');
      heartBtn.innerHTML = '<i class="fa-regular fa-heart"></i>';
      heartBtn.setAttribute('data-favorited', 'false');
      removeFavorite(show.mal_id);
      postErrorMessage(102, "Removed Favorite", `Removed "${show.name}" from favorites`);
    }, { once: true });
  };
  const cancelLongPress = () => {
    if (pressTimer) clearTimeout(pressTimer);
    heartBtn.classList.remove('holding');
    isLongPress = false;
  };
  const handlePointerDown = (e) => {
    e.preventDefault();
    isLongPress = false;
    heartBtn.classList.add('holding');
    pressTimer = setTimeout(() => { isLongPress = true; removeFavoriteBtnFunc(); }, 800);
  };
  const handlePointerUp = () => {
    if (pressTimer) clearTimeout(pressTimer);
    if (!isLongPress) heartBtn.classList.remove('holding');
    isLongPress = false;
  };
  const handleClickInactive = (e) => { e.stopPropagation(); e.preventDefault(); addFavoriteBtnFunc(); };
  function updateHeartListeners() {
    const isFavorited = heartBtn.getAttribute('data-favorited') === 'true';
    heartBtn.removeEventListener('click', handleClickInactive);
    heartBtn.removeEventListener('pointerdown', handlePointerDown);
    heartBtn.removeEventListener('pointerup', handlePointerUp);
    heartBtn.removeEventListener('pointercancel', cancelLongPress);
    heartBtn.removeEventListener('pointerleave', cancelLongPress);
    if (!isFavorited) {
      heartBtn.addEventListener('click', handleClickInactive);
    } else {
      heartBtn.addEventListener('pointerdown', handlePointerDown);
      heartBtn.addEventListener('pointerup', handlePointerUp);
      heartBtn.addEventListener('pointercancel', cancelLongPress);
      heartBtn.addEventListener('pointerleave', cancelLongPress);
      heartBtn.addEventListener('click', (e) => e.preventDefault());
    }
  }
  updateHeartListeners();
  const origSetAttr = heartBtn.setAttribute.bind(heartBtn);
  heartBtn.setAttribute = (name, val) => { origSetAttr(name, val); if (name === 'data-favorited') updateHeartListeners(); };

  // Expand arrow event
  const arrowBtn = card.querySelector('.expand-arrow');
  arrowBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    card.classList.toggle('expanded');
    if (card.classList.contains('expanded')) {
      card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  });

  // Card click navigation (exclude heart, arrow, chat)
  card.addEventListener('click', (e) => {
    if (!e.target.closest('.favorite-heart') && !e.target.closest('.expand-arrow') && !e.target.closest('.chat-icon')) {
      window.location.href = `/anime/${show.mal_id}`;
    }
  });

  return card;
}

// Escape HTML
function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
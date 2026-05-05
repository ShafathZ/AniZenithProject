const STORAGE_KEY = 'anizenith_favorites';

function getStore() {
  const raw = localStorage.getItem(STORAGE_KEY);
  return raw ? JSON.parse(raw) : {};
}

function setStore(store) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
}

export function getFavorites() {
  return Object.values(getStore());
}

export function saveFavorites(favoritesArray) {
  const store = {};
  favoritesArray.forEach(anime => { if (anime?.mal_id) store[anime.mal_id] = anime; });
  setStore(store);
}

export function isAnimeFavorited(id) {
  return getStore().hasOwnProperty(id);
}

export function addFavorite(anime) {
  const store = getStore();
  if (!store[anime.mal_id]) {
    store[anime.mal_id] = anime;
    setStore(store);
    window.dispatchEvent(new CustomEvent('favoritesUpdated', { detail: Object.values(store) }));
  }
}

export function removeFavorite(id) {
  const store = getStore();
  if (store[id]) {
    delete store[id];
    setStore(store);
    window.dispatchEvent(new CustomEvent('favoritesUpdated', { detail: Object.values(store) }));
  }
}
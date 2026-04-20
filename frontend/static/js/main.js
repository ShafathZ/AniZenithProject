import { postErrorMessage } from "./error.js"

document.addEventListener("DOMContentLoaded", () => {
    // ===== SIDEBAR =====
    const sidebar = document.getElementById("sidebar");

    sidebar.addEventListener('click', () => {
        sidebar.classList.add('expanded');
        sidebar.classList.remove('collapsed');
    });

    document.addEventListener('click', (e) => {
        const toggleBtn = document.getElementById('sidebarToggle');
        if (toggleBtn && toggleBtn.contains(e.target)) return;
        if (!sidebar.contains(e.target)) {
            sidebar.classList.remove('expanded');
            sidebar.classList.add('collapsed');
        }
    });

    // ===== HAMBURGER =====
    const hamburger = document.getElementById('sidebarToggle');
    if (hamburger) {
        hamburger.addEventListener('click', (e) => {
            e.stopPropagation();
            if (sidebar.classList.contains('collapsed')) {
                sidebar.classList.remove('collapsed');
                sidebar.classList.add('expanded');
            } else {
                sidebar.classList.add('collapsed');
                sidebar.classList.remove('expanded');
            }
        });
    }

    // ===== SEARCH BAR =====
    const searchInput = document.querySelector('#search-input');
    const searchIconBtn = document.querySelector('.search-icon-btn');
    const filterBtn = document.querySelector('.filter-redirect-btn');

    // Function to redirect with query
    function performSearch() {
        const query = searchInput.value.trim();
        window.location.href = query ? `/search?q=${encodeURIComponent(query)}` : '/search';
    }
    searchIconBtn.addEventListener('click', performSearch);
    filterBtn.addEventListener('click', performSearch);

    // Enter redirects to /search endpoint
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            performSearch();
        }
    });

    // ===== LANGUAGE =====
    const langToggle = document.getElementById('langToggle');
    const langOptions = document.querySelectorAll('#langToggle .lang-option');

    function setLang(lang) {
      langOptions.forEach(btn =>
        btn.classList.toggle('active', btn.dataset.lang === lang)
      );

      localStorage.setItem('preferredLanguage', lang);
      document.dispatchEvent(
        new CustomEvent('languageChange', { detail: { language: lang } })
      );
    }

    langToggle?.addEventListener('click', () => {
      const active = document.querySelector('#langToggle .lang-option.active');
      const nextLang = active.dataset.lang === 'en' ? 'jp' : 'en';
      setLang(nextLang);
    });

    // Get language from local cached
    setLang(localStorage.getItem('preferredLanguage') || 'en');

    // ===== RANDOM =====
    const randomBtn = document.getElementById('randomAnimeBtn');
    randomBtn.addEventListener('click', () => {
        postErrorMessage(300, "Unsupported Operation", "Random Button is not yet Supported");
    });
});
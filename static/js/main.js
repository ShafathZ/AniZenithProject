document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("sidebar");

    // Adds toggle for sidebar
    sidebar.addEventListener('click', () => {
        sidebar.classList.add('expanded');
    });

    document.addEventListener('click', (e) => {
        if (!sidebar.contains(e.target)) {
            sidebar.classList.remove('expanded');
            sidebar.classList.add('collapsed');
        }
    });
});
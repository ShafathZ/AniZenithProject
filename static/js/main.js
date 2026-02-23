document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("sidebar");

    // Adds toggle for sidebar by expanding it when it is clicked
    sidebar.addEventListener('click', () => {
        sidebar.classList.add('expanded');
    });

    // If anywhere else in document is clicked, collapses sidebar
    document.addEventListener('click', (e) => {
        if (!sidebar.contains(e.target)) {
            sidebar.classList.remove('expanded');
            sidebar.classList.add('collapsed');
        }
    });
});
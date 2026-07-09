// Runs immediately (this file is loaded without `defer` in <head>) so the
// saved theme is applied to <html> before first paint - no flash of the
// wrong theme.
(function () {
    var saved = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
})();

document.addEventListener('DOMContentLoaded', function () {
    var root = document.documentElement;

    // --- Theme toggle ---
    var themeToggle = document.getElementById('theme-toggle');

    function paintThemeIcon(theme) {
        if (themeToggle) {
            themeToggle.textContent = theme === 'light' ? '☀️' : '🌙';
        }
    }
    paintThemeIcon(root.getAttribute('data-theme') || 'dark');

    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            var next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
            root.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            paintThemeIcon(next);
        });
    }

    // --- Mobile menu (hamburger) ---
    var menuToggle = document.getElementById('menu-toggle');
    var navbar = document.querySelector('.navbar');

    if (menuToggle && navbar) {
        menuToggle.addEventListener('click', function () {
            var isOpen = navbar.classList.toggle('nav-open');
            menuToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });
    }
});
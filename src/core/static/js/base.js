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

    // --- Teaser and closing videos: one <video> each, its source follows the theme ---
    function paintVideos(theme) {
        document.querySelectorAll('video[data-' + theme + ']').forEach(function (video) {
            var src = video.getAttribute('data-' + theme);
            if (video.getAttribute('src') === src) return;
            var time = video.currentTime;
            var playing = video.autoplay || !video.paused;
            video.setAttribute('src', src);
            video.addEventListener('loadedmetadata', function () {
                video.currentTime = time;
            }, { once: true });
            if (playing) video.play().catch(function () {});
        });
    }
    // --- Chapter animations: each GIF and its video link have a dark and a light render ---
    function paintAnimations(theme) {
        document.querySelectorAll('figure.video [data-' + theme + ']').forEach(function (el) {
            var attr = el.tagName === 'A' ? 'href' : 'src';
            var url = el.getAttribute('data-' + theme);
            if (el.getAttribute(attr) !== url) el.setAttribute(attr, url);
        });
    }

    paintVideos(root.getAttribute('data-theme') || 'dark');
    paintAnimations(root.getAttribute('data-theme') || 'dark');

    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            var next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
            root.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            paintThemeIcon(next);
            paintVideos(next);
            paintAnimations(next);
        });
    }

    // --- Syntax highlighting (highlight.js is loaded with defer from cdnjs) ---
    if (window.hljs) {
        document.querySelectorAll('pre code[class^="language-"]').forEach(function (el) {
            if (!el.classList.contains('out') && !el.classList.contains('language-plaintext')) {
                window.hljs.highlightElement(el);
            }
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
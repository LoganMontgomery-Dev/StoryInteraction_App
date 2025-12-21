/* ============================================================================
   DOAMMO UI - Theme Management
   ============================================================================ */

function setTheme(themeName) {
    document.documentElement.setAttribute('data-theme', themeName);
    localStorage.setItem('doammo-theme', themeName);

    // Update theme buttons
    document.querySelectorAll('.theme-btn').forEach(btn => {
        if (btn.getAttribute('data-theme') === themeName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

function loadTheme() {
    const savedTheme = localStorage.getItem('doammo-theme') || 'doammo';
    setTheme(savedTheme);
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', () => {
    loadTheme();

    // Add theme button click handlers
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const theme = btn.getAttribute('data-theme');
            setTheme(theme);
        });
    });
});

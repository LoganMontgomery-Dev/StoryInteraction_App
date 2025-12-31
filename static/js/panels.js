/* ============================================================================
   DOAMMO UI - Panel Management (Resize & Collapse)
   ============================================================================ */

let isResizing = false;
let storyCollapsed = false;
let directorCollapsed = false;

// Panel resizing
document.addEventListener('DOMContentLoaded', () => {
    const dragHandle = document.getElementById('dragHandle');
    const storyPanel = document.querySelector('.story-panel');
    const directorPanel = document.getElementById('directorPanel');
    const mainContainer = document.querySelector('.main-container');
    const storyRestoreTab = document.getElementById('storyRestoreTab');
    const directorRestoreTab = document.getElementById('directorRestoreTab');

    // Load saved panel width
    const savedWidth = localStorage.getItem('doammo-story-panel-width');
    if (savedWidth) {
        storyPanel.style.width = savedWidth;
    }

    // Load saved collapse states
    const savedStoryCollapsed = localStorage.getItem('doammo-story-collapsed') === 'true';
    const savedDirectorCollapsed = localStorage.getItem('doammo-director-collapsed') === 'true';

    if (savedStoryCollapsed) {
        collapseStoryPanel();
    }
    if (savedDirectorCollapsed) {
        collapseDirectorPanel();
    }

    dragHandle.addEventListener('mousedown', (e) => {
        if (storyCollapsed || directorCollapsed) return; // Don't resize when collapsed
        isResizing = true;
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
    });

    document.addEventListener('mousemove', (e) => {
        if (!isResizing) return;

        const containerRect = mainContainer.getBoundingClientRect();
        const newWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;

        // Check for collapse thresholds
        if (newWidth <= 5) {
            // Collapse story panel
            collapseStoryPanel();
            isResizing = false;
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
            return;
        } else if (newWidth >= 95) {
            // Collapse director panel
            collapseDirectorPanel();
            isResizing = false;
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
            return;
        }

        // Normal resize within bounds (10% - 90%)
        if (newWidth >= 10 && newWidth <= 90) {
            storyPanel.style.width = `${newWidth}%`;
            directorPanel.style.width = `${100 - newWidth}%`;
        }
    });

    document.addEventListener('mouseup', () => {
        if (isResizing) {
            isResizing = false;
            document.body.style.cursor = '';
            document.body.style.userSelect = '';

            // Save panel width
            if (!storyCollapsed && !directorCollapsed) {
                localStorage.setItem('doammo-story-panel-width', storyPanel.style.width);
            }
        }
    });

    // Story panel restore tab click
    if (storyRestoreTab) {
        storyRestoreTab.addEventListener('click', restoreStoryPanel);
    }

    // Director panel restore tab click
    if (directorRestoreTab) {
        directorRestoreTab.addEventListener('click', restoreDirectorPanel);
    }

    // Old collapse button (keep for backwards compatibility, now toggles director)
    const collapseBtn = document.getElementById('collapseBtn');
    if (collapseBtn) {
        collapseBtn.addEventListener('click', () => {
            if (directorCollapsed) {
                restoreDirectorPanel();
            } else {
                collapseDirectorPanel();
            }
        });
    }

    // Tab switching
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');

            // Update buttons
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update content
            tabContents.forEach(content => {
                if (content.id === targetTab) {
                    content.classList.add('active');
                } else {
                    content.classList.remove('active');
                }
            });
        });
    });
});

// Collapse story panel (slide to left edge)
function collapseStoryPanel() {
    const storyPanel = document.querySelector('.story-panel');
    const directorPanel = document.getElementById('directorPanel');
    const dragHandle = document.getElementById('dragHandle');
    const storyRestoreTab = document.getElementById('storyRestoreTab');

    storyCollapsed = true;
    storyPanel.classList.add('collapsed');
    storyPanel.style.width = '0';
    directorPanel.style.width = '100%';
    dragHandle.style.display = 'none';

    if (storyRestoreTab) {
        storyRestoreTab.style.display = 'flex';
    }

    localStorage.setItem('doammo-story-collapsed', 'true');
}

// Restore story panel
function restoreStoryPanel() {
    const storyPanel = document.querySelector('.story-panel');
    const directorPanel = document.getElementById('directorPanel');
    const dragHandle = document.getElementById('dragHandle');
    const storyRestoreTab = document.getElementById('storyRestoreTab');

    storyCollapsed = false;
    storyPanel.classList.remove('collapsed');

    const savedWidth = localStorage.getItem('doammo-story-panel-width') || '50%';
    storyPanel.style.width = savedWidth;

    const storyWidth = parseFloat(savedWidth);
    directorPanel.style.width = `${100 - storyWidth}%`;

    dragHandle.style.display = '';

    if (storyRestoreTab) {
        storyRestoreTab.style.display = 'none';
    }

    localStorage.setItem('doammo-story-collapsed', 'false');
}

// Collapse director panel (slide to right edge)
function collapseDirectorPanel() {
    const storyPanel = document.querySelector('.story-panel');
    const directorPanel = document.getElementById('directorPanel');
    const dragHandle = document.getElementById('dragHandle');
    const directorRestoreTab = document.getElementById('directorRestoreTab');
    const collapseBtn = document.getElementById('collapseBtn');

    directorCollapsed = true;
    directorPanel.classList.add('collapsed');
    directorPanel.style.width = '0';
    storyPanel.style.width = '100%';
    dragHandle.style.display = 'none';

    if (directorRestoreTab) {
        directorRestoreTab.style.display = 'flex';
    }

    if (collapseBtn) {
        const chevron = collapseBtn.querySelector('i, svg');
        if (chevron) chevron.style.transform = 'rotate(180deg)';
    }

    localStorage.setItem('doammo-director-collapsed', 'true');
}

// Restore director panel
function restoreDirectorPanel() {
    const storyPanel = document.querySelector('.story-panel');
    const directorPanel = document.getElementById('directorPanel');
    const dragHandle = document.getElementById('dragHandle');
    const directorRestoreTab = document.getElementById('directorRestoreTab');
    const collapseBtn = document.getElementById('collapseBtn');

    directorCollapsed = false;
    directorPanel.classList.remove('collapsed');

    const savedWidth = localStorage.getItem('doammo-story-panel-width') || '50%';
    const storyWidth = parseFloat(savedWidth);
    storyPanel.style.width = savedWidth;
    directorPanel.style.width = `${100 - storyWidth}%`;

    dragHandle.style.display = '';

    if (directorRestoreTab) {
        directorRestoreTab.style.display = 'none';
    }

    if (collapseBtn) {
        const chevron = collapseBtn.querySelector('i, svg');
        if (chevron) chevron.style.transform = 'rotate(0deg)';
    }

    localStorage.setItem('doammo-director-collapsed', 'false');
}

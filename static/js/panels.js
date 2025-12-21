/* ============================================================================
   DOAMMO UI - Panel Management (Resize & Collapse)
   ============================================================================ */

let isResizing = false;
let directorCollapsed = false;

// Panel resizing
document.addEventListener('DOMContentLoaded', () => {
    const dragHandle = document.getElementById('dragHandle');
    const storyPanel = document.querySelector('.story-panel');
    const directorPanel = document.getElementById('directorPanel');
    const mainContainer = document.querySelector('.main-container');

    // Load saved panel width
    const savedWidth = localStorage.getItem('doammo-story-panel-width');
    if (savedWidth) {
        storyPanel.style.width = savedWidth;
    }

    dragHandle.addEventListener('mousedown', (e) => {
        isResizing = true;
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
    });

    document.addEventListener('mousemove', (e) => {
        if (!isResizing) return;

        const containerRect = mainContainer.getBoundingClientRect();
        const newWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;

        // Enforce constraints (30% - 70%)
        if (newWidth >= 30 && newWidth <= 70) {
            storyPanel.style.width = `${newWidth}%`;
            if (!directorCollapsed) {
                directorPanel.style.width = `${100 - newWidth}%`;
            }
        }
    });

    document.addEventListener('mouseup', () => {
        if (isResizing) {
            isResizing = false;
            document.body.style.cursor = '';
            document.body.style.userSelect = '';

            // Save panel width
            localStorage.setItem('doammo-story-panel-width', storyPanel.style.width);
        }
    });

    // Panel collapse
    const collapseBtn = document.getElementById('collapseBtn');
    const directorContent = document.querySelector('.director-content');

    collapseBtn.addEventListener('click', () => {
        directorCollapsed = !directorCollapsed;

        if (directorCollapsed) {
            directorPanel.classList.add('collapsed');
            directorPanel.style.width = '40px';
            const chevron = collapseBtn.querySelector('i');
            chevron.style.transform = 'rotate(180deg)';
        } else {
            directorPanel.classList.remove('collapsed');
            const savedWidth = localStorage.getItem('doammo-story-panel-width') || '50%';
            const storyWidth = parseFloat(savedWidth);
            directorPanel.style.width = `${100 - storyWidth}%`;
            const chevron = collapseBtn.querySelector('i');
            chevron.style.transform = 'rotate(0deg)';
        }
    });

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

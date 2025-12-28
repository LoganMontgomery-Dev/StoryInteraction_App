/* ============================================================================
   DOAMMO UI - Settings Modal Management
   ============================================================================ */

document.addEventListener('DOMContentLoaded', () => {
    const settingsModal = document.getElementById('settingsModal');
    const closeModal = document.getElementById('closeModal');

    // Open modal - use event delegation to handle Lucide icon replacement
    document.addEventListener('click', (e) => {
        // Check if click target is settings icon or its child SVG
        const settingsIcon = e.target.closest('#settingsIcon');
        if (settingsIcon) {
            e.stopPropagation();
            if (settingsModal) {
                settingsModal.classList.add('active');
                lucide.createIcons(); // Reinitialize icons in modal
            }
        }
    });

    // Close modal - X button (use event delegation for Lucide icon)
    document.addEventListener('click', (e) => {
        const closeBtn = e.target.closest('#closeModal');
        if (closeBtn) {
            e.stopPropagation();
            if (settingsModal) {
                settingsModal.classList.remove('active');
            }
        }
    });

    // Close on overlay click
    if (settingsModal) {
        settingsModal.addEventListener('click', (e) => {
            if (e.target === settingsModal) {
                settingsModal.classList.remove('active');
            }
        });
    }

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && settingsModal.classList.contains('active')) {
            settingsModal.classList.remove('active');
        }
    });

    // Accordion functionality
    const accordionHeaders = document.querySelectorAll('.accordion-header');

    accordionHeaders.forEach(header => {
        header.addEventListener('click', () => {
            // Don't expand locked sections
            if (header.classList.contains('locked')) {
                return;
            }

            const section = header.parentElement;
            const isExpanded = section.classList.contains('expanded');

            if (isExpanded) {
                section.classList.remove('expanded');
            } else {
                section.classList.add('expanded');
            }

            // Reinitialize icons after accordion animation
            setTimeout(() => {
                lucide.createIcons();
            }, 50);
        });
    });
});

/* ============================================================================
   DOAMMO UI - Settings Modal Management
   ============================================================================ */

document.addEventListener('DOMContentLoaded', () => {
    const settingsModal = document.getElementById('settingsModal');
    const closeModal = document.getElementById('closeModal');

    // Wait for Lucide to initialize icons, then attach event listeners
    setTimeout(() => {
        const settingsIcon = document.getElementById('settingsIcon');

        if (settingsIcon) {
            // Open modal
            settingsIcon.addEventListener('click', () => {
                settingsModal.classList.add('active');
                lucide.createIcons(); // Reinitialize icons in modal
            });
        }

        // Close modal
        if (closeModal) {
            closeModal.addEventListener('click', () => {
                settingsModal.classList.remove('active');
            });
        }
    }, 100);

    // Close on overlay click
    settingsModal.addEventListener('click', (e) => {
        if (e.target === settingsModal) {
            settingsModal.classList.remove('active');
        }
    });

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

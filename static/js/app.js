/* ============================================================================
   DOAMMO UI - Main Application Logic
   ============================================================================ */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide icons
    lucide.createIcons();

    // Export Modal
    const exportBtn = document.getElementById('exportBtn');
    const exportModal = document.getElementById('exportModal');
    const closeExportModal = document.getElementById('closeExportModal');

    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            exportModal.style.display = 'flex';
            lucide.createIcons();
        });
    }

    if (closeExportModal) {
        closeExportModal.addEventListener('click', () => {
            exportModal.style.display = 'none';
        });
    }

    // Close modal on overlay click
    if (exportModal) {
        exportModal.addEventListener('click', (e) => {
            if (e.target === exportModal) {
                exportModal.style.display = 'none';
            }
        });
    }
});

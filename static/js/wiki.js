/* ============================================================================
   DOAMMO UI - Story Wiki (Mockup - Frontend Only)
   ============================================================================ */

let currentWiki = null; // Track currently loaded wiki

// ============================================================================
// Wiki Management
// ============================================================================

function openWikiBrowserModal() {
    const modal = document.getElementById('wikiBrowserModal');
    modal.classList.add('active');
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function closeWikiBrowserModal() {
    const modal = document.getElementById('wikiBrowserModal');
    modal.classList.remove('active');
}

function openSaveWikiModal() {
    const modal = document.getElementById('saveWikiModal');
    modal.classList.add('active');
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function closeSaveWikiModal() {
    const modal = document.getElementById('saveWikiModal');
    modal.classList.remove('active');
}

function openWiki(wikiName) {
    currentWiki = wikiName;

    // Update status indicator
    const wikiStatus = document.getElementById('wikiStatus');
    wikiStatus.innerHTML = `
        <i data-lucide="folder" style="width: 14px; height: 14px;"></i>
        ${wikiName.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
    `;
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    closeWikiBrowserModal();

    alert(`Mockup: Loaded wiki "${wikiName}"\nIn real implementation, this would load the conversation history and wiki pages.`);
}

function saveToWiki() {
    const wikiName = document.getElementById('wikiNameInput').value.trim();
    const wikiPath = document.getElementById('wikiPathInput').value;

    if (!wikiName) {
        alert('Please enter a wiki name');
        return;
    }

    currentWiki = wikiName;

    // Update status indicator
    const wikiStatus = document.getElementById('wikiStatus');
    wikiStatus.innerHTML = `
        <i data-lucide="folder" style="width: 14px; height: 14px;"></i>
        ${wikiName}
    `;
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    closeSaveWikiModal();

    alert(`Mockup: Saved to wiki "${wikiName}"\nLocation: ${wikiPath}${wikiName}\n\nIn real implementation, this would:\n- Create wiki folder structure\n- Save conversation history\n- Create initial wiki pages`);
}

function browseWikiLocation() {
    alert('Mockup: File browser would open here\nIn real implementation, this would let you choose a folder location.');
}

function browseForWiki() {
    alert('Mockup: File browser would open here\nIn real implementation, this would let you browse your file system to find and open any wiki folder.');
}

// ============================================================================
// Notifications Modal
// ============================================================================

function openNotificationsModal() {
    const modal = document.getElementById('notificationsModal');
    modal.classList.add('active');
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function closeNotificationsModal() {
    const modal = document.getElementById('notificationsModal');
    modal.classList.remove('active');
}

// ============================================================================
// Profile Modal
// ============================================================================

function openProfileModal() {
    const modal = document.getElementById('profileModal');
    modal.classList.add('active');
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function closeProfileModal() {
    const modal = document.getElementById('profileModal');
    modal.classList.remove('active');
}

// ============================================================================
// Lore Viewer
// ============================================================================

// Mockup: View lore file details
function viewLoreFile(filename) {
    const detailCard = document.getElementById('loreDetailCard');
    const detailTitle = document.getElementById('loreDetailTitle');
    const detailContent = document.getElementById('loreDetailContent');

    // Show the detail card
    detailCard.style.display = 'block';
    detailTitle.textContent = filename;

    // Mockup content (in real implementation, this would fetch from backend)
    const mockupContent = {
        'Lyssia.md': `# Lyssia

## Overview
Lyssia is one of the primary characters in the DOAMMO universe. She is a skilled explorer and researcher who has dedicated her life to understanding the mysteries of the ancient world.

## Background
Born in the settlements near the edge of the Dust, Lyssia grew up hearing stories of the old world and the artifacts that remained buried beneath the sands.

## Personality
- Curious and methodical
- Strong sense of justice
- Resourceful in difficult situations
- Values knowledge and preservation of history

## Skills
- Archaeological expertise
- Ancient language translation
- Survival skills in harsh environments`,

        'Ancient_Ruins.md': `# Ancient Ruins

## Description
Scattered throughout the world are remnants of a civilization that came before. These ruins hold secrets, technology, and dangers in equal measure.

## Notable Locations
- The Temple of Echoes
- The Submerged Archive
- The Sky Towers

## Dangers
Many ruins are protected by automated defenses or have been claimed by dangerous creatures. Exploration requires careful preparation.

## Artifacts
The ruins contain various artifacts from the old world, including:
- Data crystals
- Power cells
- Ancient texts
- Technological fragments`,

        'The_Dust.md': `# The Dust

## Overview
The Dust is the name given to the mysterious atmospheric phenomenon that covers much of the world. It blocks out sunlight, creating a perpetual twilight.

## Properties
- Appears as a fine, shimmering particulate matter
- Reduces visibility significantly
- Affects electronic equipment in unpredictable ways
- Source and nature remain largely unknown

## Impact on Society
The Dust has shaped civilization, forcing settlements to adapt to low-light conditions and rely on alternative energy sources.`
    };

    // Display the mockup content
    detailContent.textContent = mockupContent[filename] || 'Content not found in mockup data.';

    // Scroll to detail card
    detailCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    // Reinitialize icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// Close lore detail view
function closeLoreDetail() {
    const detailCard = document.getElementById('loreDetailCard');
    detailCard.style.display = 'none';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Story Wiki mockup loaded');

    // Get all elements
    const openWikiBtn = document.getElementById('openWikiBtn');
    const saveWikiBtn = document.getElementById('saveWikiBtn');
    const closeWikiBrowserBtn = document.getElementById('closeWikiBrowserModal');
    const closeSaveWikiBtn = document.getElementById('closeSaveWikiModal');
    const notificationsIcon = document.getElementById('notificationsIcon');
    const profileIcon = document.getElementById('profileIcon');
    const closeNotificationsBtn = document.getElementById('closeNotificationsModal');
    const closeProfileBtn = document.getElementById('closeProfileModal');

    // Open wiki buttons
    if (openWikiBtn) {
        openWikiBtn.addEventListener('click', openWikiBrowserModal);
    }

    if (saveWikiBtn) {
        saveWikiBtn.addEventListener('click', openSaveWikiModal);
    }

    // Close buttons (X icons)
    if (closeWikiBrowserBtn) {
        closeWikiBrowserBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closeWikiBrowserModal();
        });
    }

    if (closeSaveWikiBtn) {
        closeSaveWikiBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closeSaveWikiModal();
        });
    }

    if (closeNotificationsBtn) {
        closeNotificationsBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closeNotificationsModal();
        });
    }

    if (closeProfileBtn) {
        closeProfileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closeProfileModal();
        });
    }

    // Top bar icons
    if (notificationsIcon) {
        notificationsIcon.addEventListener('click', openNotificationsModal);
    }

    if (profileIcon) {
        profileIcon.addEventListener('click', openProfileModal);
    }

    // Close modals on overlay click
    const wikiBrowserModal = document.getElementById('wikiBrowserModal');
    const saveWikiModal = document.getElementById('saveWikiModal');
    const notificationsModal = document.getElementById('notificationsModal');
    const profileModal = document.getElementById('profileModal');

    if (wikiBrowserModal) {
        wikiBrowserModal.addEventListener('click', (e) => {
            if (e.target === wikiBrowserModal) {
                closeWikiBrowserModal();
            }
        });
    }

    if (saveWikiModal) {
        saveWikiModal.addEventListener('click', (e) => {
            if (e.target === saveWikiModal) {
                closeSaveWikiModal();
            }
        });
    }

    if (notificationsModal) {
        notificationsModal.addEventListener('click', (e) => {
            if (e.target === notificationsModal) {
                closeNotificationsModal();
            }
        });
    }

    if (profileModal) {
        profileModal.addEventListener('click', (e) => {
            if (e.target === profileModal) {
                closeProfileModal();
            }
        });
    }
});

/**
 * Lore Keeper - Automatic lore extraction from narratives
 */

// Lore Keeper state
let loreKeeperEnabled = false;
let loreKeeperConfirmRequired = true;
let extractedLoreData = null;
let selectedEntities = { characters: [], locations: [], items: [], events: [] };
let editingEntity = null; // Track which entity is being edited

// Initialize Lore Keeper
function initLoreKeeper() {
    // Load saved preferences
    const savedEnabled = localStorage.getItem('loreKeeperEnabled');
    const savedConfirm = localStorage.getItem('loreKeeperConfirm');

    if (savedEnabled !== null) {
        loreKeeperEnabled = savedEnabled === 'true';
    }
    if (savedConfirm !== null) {
        loreKeeperConfirmRequired = savedConfirm === 'true';
    }

    // Set UI state
    const enabledToggle = document.getElementById('loreKeeperEnabled');
    const confirmToggle = document.getElementById('loreKeeperConfirm');

    if (enabledToggle) {
        enabledToggle.checked = loreKeeperEnabled;
        enabledToggle.addEventListener('change', (e) => {
            loreKeeperEnabled = e.target.checked;
            localStorage.setItem('loreKeeperEnabled', loreKeeperEnabled);
            console.log('Lore Keeper enabled:', loreKeeperEnabled);
        });
    }

    if (confirmToggle) {
        confirmToggle.checked = loreKeeperConfirmRequired;
        confirmToggle.addEventListener('change', (e) => {
            loreKeeperConfirmRequired = e.target.checked;
            localStorage.setItem('loreKeeperConfirm', loreKeeperConfirmRequired);
            console.log('Lore Keeper confirm required:', loreKeeperConfirmRequired);
        });
    }

    console.log('Lore Keeper initialized - enabled:', loreKeeperEnabled, 'confirm:', loreKeeperConfirmRequired);
}

// Get current lore keeper mode (for compatibility)
function getLoreKeeperMode() {
    if (!loreKeeperEnabled) return 'off';
    return loreKeeperConfirmRequired ? 'confirm' : 'auto';
}

// Extract lore from a single narrative response
async function extractLoreFromNarrative(narrative) {
    const mode = getLoreKeeperMode();
    console.log('extractLoreFromNarrative called, mode:', mode);

    if (mode === 'off') {
        console.log('Lore Keeper is off, skipping');
        return null;
    }
    if (!currentWiki) {
        console.log('No wiki loaded, skipping lore extraction');
        return null;
    }

    console.log('Extracting lore from narrative...');

    try {
        // Get existing entities to avoid duplicates
        const existingResponse = await fetch(`${API_URL}/wiki/${currentWiki}/existing-entities`);
        const existingData = await existingResponse.json();
        const existingEntities = existingData.success ? existingData.entities : null;

        // Extract lore
        const response = await fetch(`${API_URL}/lore/extract`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                narrative: narrative,
                existing_entities: existingEntities
            })
        });

        const data = await response.json();
        if (!data.success) {
            console.error('Lore extraction failed:', data);
            return null;
        }

        const extracted = data.extracted;
        const hasEntities = Object.values(extracted).some(arr => arr.length > 0);

        if (!hasEntities) {
            console.log('No new lore entities found');
            return null;
        }

        if (mode === 'auto') {
            // Auto-save without confirmation
            await saveLoreToWiki(extracted);
            showNotification(`Lore Keeper saved ${countEntities(extracted)} entities`);
        } else if (mode === 'confirm') {
            // Show in the Lore Keeper panel
            showExtractedLorePanel(extracted);
        }

        return extracted;
    } catch (error) {
        console.error('Error extracting lore:', error);
        return null;
    }
}

// Scan entire conversation for lore (manual trigger)
async function scanConversationForLore() {
    if (!sessionId) {
        showNotification('No active session to scan', 'error');
        return;
    }

    if (!currentWiki) {
        showNotification('Please load a wiki first', 'error');
        return;
    }

    // Show loading state on button
    const scanBtn = document.getElementById('scanConversationBtn');
    if (scanBtn) {
        scanBtn.disabled = true;
        scanBtn.innerHTML = `
            <i data-lucide="loader-2" style="width: 14px; height: 14px;" class="spin"></i>
            Scanning...
        `;
        lucide.createIcons();
    }

    try {
        // Get existing entities
        const existingResponse = await fetch(`${API_URL}/wiki/${currentWiki}/existing-entities`);
        const existingData = await existingResponse.json();
        const existingEntities = existingData.success ? existingData.entities : null;

        // Extract from session
        const response = await fetch(`${API_URL}/lore/extract-session/${sessionId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ existing_entities: existingEntities })
        });

        const data = await response.json();

        if (!data.success) {
            showNotification('Failed to extract lore', 'error');
            return;
        }

        const hasEntities = Object.values(data.extracted).some(arr => arr.length > 0);

        if (!hasEntities) {
            showNotification('No new lore found in conversation', 'info');
            return;
        }

        showExtractedLorePanel(data.extracted);
    } catch (error) {
        console.error('Error scanning conversation:', error);
        showNotification('Error scanning conversation', 'error');
    } finally {
        // Reset button
        if (scanBtn) {
            scanBtn.disabled = false;
            scanBtn.innerHTML = `
                <i data-lucide="scan-search" style="width: 14px; height: 14px;"></i>
                Scan Conversation Now
            `;
            lucide.createIcons();
        }
    }
}

// Show extracted lore in the panel
function showExtractedLorePanel(extracted) {
    extractedLoreData = extracted;
    selectedEntities = { characters: [], locations: [], items: [], events: [] };

    const panel = document.getElementById('extractedLorePanel');
    const content = document.getElementById('extractedLoreContent');

    if (!panel || !content) {
        console.error('Extracted lore panel not found');
        return;
    }

    const hasEntities = Object.values(extracted).some(arr => arr.length > 0);

    if (!hasEntities) {
        content.innerHTML = '<p style="color: var(--secondary-text);">No new lore entities found.</p>';
        panel.style.display = 'block';
        return;
    }

    // Build the content
    let html = '';

    const categories = [
        { key: 'characters', icon: 'user', label: 'Characters' },
        { key: 'locations', icon: 'map-pin', label: 'Locations' },
        { key: 'items', icon: 'sword', label: 'Items' },
        { key: 'events', icon: 'calendar', label: 'Events' }
    ];

    categories.forEach(({ key, icon, label }) => {
        const entities = extracted[key] || [];
        if (entities.length === 0) return;

        html += `
            <div class="lore-extraction-category" id="extracted${label}">
                <div class="category-header">
                    <i data-lucide="${icon}" style="width: 16px; height: 16px;"></i>
                    ${label}
                    <span class="category-count">${entities.length}</span>
                </div>
                <div class="category-items">
        `;

        entities.forEach((entity, index) => {
            // Add to selected by default
            selectedEntities[key].push(index);

            html += `
                <div class="lore-entity-item selected" data-category="${key}" data-index="${index}">
                    <div class="entity-checkbox" onclick="toggleEntitySelection(this.parentElement, '${key}', ${index})">
                        <i data-lucide="check" style="width: 14px; height: 14px;"></i>
                    </div>
                    <div class="entity-info" id="entity-info-${key}-${index}">
                        <div class="entity-name">${escapeHtml(entity.name)}</div>
                        <div class="entity-description">${escapeHtml(entity.description)}</div>
                    </div>
                    <div class="entity-actions">
                        <button class="entity-edit-btn" onclick="editEntity('${key}', ${index})" title="Edit">
                            <i data-lucide="pencil" style="width: 14px; height: 14px;"></i>
                        </button>
                    </div>
                </div>
            `;
        });

        html += '</div></div>';
    });

    content.innerHTML = html;
    panel.style.display = 'block';
    lucide.createIcons();

    // Switch to Lore Keeper tab
    switchToTab('lore-keeper');
}

// Switch to a specific tab
function switchToTab(tabId) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabId);
    });

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === tabId);
    });
}

// Toggle entity selection
function toggleEntitySelection(item, category, index) {
    item.classList.toggle('selected');

    const selectedIndex = selectedEntities[category].indexOf(index);
    if (selectedIndex > -1) {
        selectedEntities[category].splice(selectedIndex, 1);
    } else {
        selectedEntities[category].push(index);
    }

    lucide.createIcons();
}

// Edit entity
function editEntity(category, index) {
    const entity = extractedLoreData[category][index];
    if (!entity) return;

    const infoDiv = document.getElementById(`entity-info-${category}-${index}`);
    if (!infoDiv) return;

    // Store original content for cancel
    editingEntity = { category, index, original: { ...entity } };

    // Replace with edit form
    infoDiv.innerHTML = `
        <div class="entity-edit-form">
            <input type="text" class="entity-name-input" value="${escapeHtml(entity.name)}" placeholder="Name">
            <textarea class="entity-description-input" placeholder="Description">${escapeHtml(entity.description)}</textarea>
            <div class="entity-edit-actions">
                <button class="btn-small btn-save" onclick="saveEntityEdit('${category}', ${index})">
                    <i data-lucide="check" style="width: 12px; height: 12px;"></i>
                    Save
                </button>
                <button class="btn-small btn-cancel" onclick="cancelEntityEdit('${category}', ${index})">
                    <i data-lucide="x" style="width: 12px; height: 12px;"></i>
                    Cancel
                </button>
            </div>
        </div>
    `;
    lucide.createIcons();

    // Focus the name input
    const nameInput = infoDiv.querySelector('.entity-name-input');
    if (nameInput) nameInput.focus();
}

// Save entity edit
function saveEntityEdit(category, index) {
    const infoDiv = document.getElementById(`entity-info-${category}-${index}`);
    if (!infoDiv) return;

    const nameInput = infoDiv.querySelector('.entity-name-input');
    const descInput = infoDiv.querySelector('.entity-description-input');

    if (nameInput && descInput) {
        // Update the extracted data
        extractedLoreData[category][index].name = nameInput.value;
        extractedLoreData[category][index].description = descInput.value;
    }

    // Restore display mode
    const entity = extractedLoreData[category][index];
    infoDiv.innerHTML = `
        <div class="entity-name">${escapeHtml(entity.name)}</div>
        <div class="entity-description">${escapeHtml(entity.description)}</div>
    `;

    editingEntity = null;
}

// Cancel entity edit
function cancelEntityEdit(category, index) {
    const infoDiv = document.getElementById(`entity-info-${category}-${index}`);
    if (!infoDiv) return;

    // Restore original if we have it
    if (editingEntity && editingEntity.category === category && editingEntity.index === index) {
        extractedLoreData[category][index] = editingEntity.original;
    }

    // Restore display mode
    const entity = extractedLoreData[category][index];
    infoDiv.innerHTML = `
        <div class="entity-name">${escapeHtml(entity.name)}</div>
        <div class="entity-description">${escapeHtml(entity.description)}</div>
    `;

    editingEntity = null;
}

// Clear extracted lore panel
function clearExtractedLore() {
    const panel = document.getElementById('extractedLorePanel');
    if (panel) {
        panel.style.display = 'none';
    }
    extractedLoreData = null;
    selectedEntities = { characters: [], locations: [], items: [], events: [] };
    editingEntity = null;
}

// Save selected lore to wiki
async function saveSelectedLore() {
    if (!currentWiki) {
        showNotification('No wiki loaded', 'error');
        return;
    }

    // Build entities object from selections
    const entitiesToSave = {
        characters: [],
        locations: [],
        items: [],
        events: []
    };

    for (const category of ['characters', 'locations', 'items', 'events']) {
        for (const index of selectedEntities[category]) {
            if (extractedLoreData[category][index]) {
                entitiesToSave[category].push(extractedLoreData[category][index]);
            }
        }
    }

    const totalCount = countEntities(entitiesToSave);
    if (totalCount === 0) {
        showNotification('No entities selected', 'error');
        return;
    }

    const success = await saveLoreToWiki(entitiesToSave);
    if (success) {
        clearExtractedLore();
        showNotification(`Saved ${totalCount} lore entities to wiki`);

        // Refresh lore list in sidebar if function exists
        if (typeof refreshLoreList === 'function') {
            refreshLoreList();
        }
    }
}

// Save lore entities to wiki via API
async function saveLoreToWiki(entities) {
    try {
        const response = await fetch(`${API_URL}/lore/save-to-wiki/${currentWiki}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ entities: entities })
        });

        const data = await response.json();

        if (!data.success) {
            console.error('Failed to save lore:', data);
            showNotification('Failed to save lore', 'error');
            return false;
        }

        if (data.errors && data.errors.length > 0) {
            console.warn('Some entities failed to save:', data.errors);
        }

        return true;
    } catch (error) {
        console.error('Error saving lore:', error);
        showNotification('Error saving lore', 'error');
        return false;
    }
}

// Count total entities
function countEntities(entities) {
    return Object.values(entities).reduce((sum, arr) => sum + arr.length, 0);
}

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize on load
document.addEventListener('DOMContentLoaded', initLoreKeeper);

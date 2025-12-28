/* ============================================================================
   DOAMMO UI - Story Wiki (Backend Connected)
   ============================================================================ */

let currentWiki = null; // Track currently loaded wiki
let autoSyncEnabled = false; // Auto-sync toggle state
const API_URL = 'http://localhost:8000';

// ============================================================================
// Wiki Management
// ============================================================================

// Toggle auto-sync functionality
function toggleAutoSync() {
    autoSyncEnabled = !autoSyncEnabled;

    const autoSyncLabel = document.getElementById('autoSyncLabel');
    const autoSyncToggle = document.getElementById('autoSyncToggle');

    if (autoSyncEnabled) {
        autoSyncLabel.textContent = 'Auto-Sync: ON';
        autoSyncToggle.style.background = 'var(--accent-color)';
        autoSyncToggle.style.color = 'white';

        if (!currentWiki) {
            alert('Auto-sync enabled, but no wiki is loaded. Please open or create a wiki first.');
        }
    } else {
        autoSyncLabel.textContent = 'Auto-Sync: OFF';
        autoSyncToggle.style.background = '';
        autoSyncToggle.style.color = '';
    }

    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// Auto-save to wiki after AI response (called from app.js)
async function autoSaveToWiki() {
    if (!autoSyncEnabled || !currentWiki || !sessionId) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/wiki/${currentWiki}/save_session`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });

        const data = await response.json();
        // Success - silently auto-saved
    } catch (error) {
        console.error('Auto-save failed:', error);
    }
}

async function openWikiBrowserModal() {
    const modal = document.getElementById('wikiBrowserModal');

    // Fetch wiki list from backend
    try {
        const response = await fetch(`${API_URL}/wiki/list`);
        const data = await response.json();

        if (data.success) {
            // Populate wiki list
            populateWikiList(data.wikis);
        }
    } catch (error) {
        console.error('Error loading wikis:', error);
    }

    modal.classList.add('active');
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function populateWikiList(wikis) {
    const wikiList = document.getElementById('wikiList');

    if (!wikis || wikis.length === 0) {
        wikiList.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--secondary-text);">No wikis found. Create your first wiki!</div>';
        return;
    }

    wikiList.innerHTML = '';
    wikis.forEach(wiki => {
        const wikiItem = document.createElement('div');
        wikiItem.className = 'wiki-item';
        wikiItem.innerHTML = `
            <div class="wiki-item-icon">
                <i data-lucide="folder" style="width: 24px; height: 24px;"></i>
            </div>
            <div class="wiki-item-info">
                <div class="wiki-item-name">${wiki.name}</div>
                <div class="wiki-item-meta">${wiki.sessions.length} session(s) • Updated: ${new Date(wiki.updated).toLocaleDateString()}</div>
            </div>
            <div class="wiki-item-actions">
                <i data-lucide="chevron-right" style="width: 18px; height: 18px; color: var(--secondary-text);"></i>
            </div>
        `;
        wikiItem.onclick = () => openWiki(wiki.safe_name);
        wikiList.appendChild(wikiItem);
    });

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

async function openWiki(wikiName) {
    try {
        const response = await fetch(`${API_URL}/wiki/${wikiName}`);
        const data = await response.json();

        if (data.success) {
            currentWiki = wikiName;

            // Update status indicator
            const wikiStatus = document.getElementById('wikiStatus');
            wikiStatus.innerHTML = `
                <i data-lucide="folder" style="width: 16px; height: 16px;"></i>
                ${data.metadata.name}
            `;
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }

            closeWikiBrowserModal();

            // Load wiki pages into lore viewer
            loadWikiPages(data.pages);

            // Show wiki info and offer to browse sessions
            const sessionCount = data.sessions.length;
            const pageCount = Object.values(data.pages).flat().length;

            if (sessionCount > 0 && confirm(`Loaded wiki "${data.metadata.name}"\n\n${sessionCount} session(s)\n${pageCount} page(s)\n\nWiki is now active!\n\nWould you like to browse previous sessions?`)) {
                openSessionBrowser();
            }
        } else {
            alert('Failed to load wiki');
        }
    } catch (error) {
        console.error('Error loading wiki:', error);
        alert(`Error: ${error.message}`);
    }
}

async function saveToWiki() {
    const wikiName = document.getElementById('wikiNameInput').value.trim();

    if (!wikiName) {
        alert('Please enter a wiki name');
        return;
    }

    if (!sessionId) {
        alert('No active session to save');
        return;
    }

    try {
        // Check if wiki exists, create if not
        let wikiExists = false;
        try {
            const checkResponse = await fetch(`${API_URL}/wiki/${wikiName}`);
            wikiExists = checkResponse.ok;
        } catch (e) {
            wikiExists = false;
        }

        // Create wiki if it doesn't exist
        if (!wikiExists) {
            const createResponse = await fetch(`${API_URL}/wiki/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: wikiName,
                    description: ''
                })
            });

            const createData = await createResponse.json();
            if (!createData.success) {
                alert(`Failed to create wiki: ${createData.detail || 'Unknown error'}`);
                return;
            }
        }

        // Save current session to wiki
        const saveResponse = await fetch(`${API_URL}/wiki/${wikiName}/save_session`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });

        const saveData = await saveResponse.json();

        if (saveData.success) {
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
            alert(`Session saved to wiki "${wikiName}" successfully!`);
        } else {
            alert(`Failed to save: ${saveData.message || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error saving to wiki:', error);
        alert(`Error: ${error.message}`);
    }
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

// Load and display wiki pages in the lore viewer
function loadWikiPages(pages) {
    const loreList = document.getElementById('loreList');
    const loreEmptyState = document.getElementById('loreEmptyState');

    // Count total pages
    const totalPages = Object.values(pages).flat().length;

    if (totalPages === 0) {
        // Show empty state
        loreList.innerHTML = '';
        if (loreEmptyState) {
            loreEmptyState.style.display = 'block';
        }
        return;
    }

    // Hide empty state
    if (loreEmptyState) {
        loreEmptyState.style.display = 'none';
    }

    // Build lore list
    loreList.innerHTML = '';

    // Categories with their display names and icons
    const categoryInfo = {
        'characters': { display: 'Characters', icon: 'user' },
        'locations': { display: 'Locations', icon: 'map-pin' },
        'items': { display: 'Items', icon: 'box' },
        'events': { display: 'Events', icon: 'calendar' }
    };

    // Display pages by category
    for (const [category, pageNames] of Object.entries(pages)) {
        if (pageNames.length === 0) continue;

        const info = categoryInfo[category] || { display: category, icon: 'file-text' };

        pageNames.forEach(pageName => {
            const loreItem = document.createElement('div');
            loreItem.className = 'lore-item';
            loreItem.style.display = 'flex';
            loreItem.style.alignItems = 'center';
            loreItem.style.justifyContent = 'space-between';

            const headerDiv = document.createElement('div');
            headerDiv.className = 'lore-item-header';
            headerDiv.style.flex = '1';
            headerDiv.style.cursor = 'pointer';
            headerDiv.onclick = () => viewLoreFile(`${category}/${pageName}.md`);
            headerDiv.innerHTML = `
                <i data-lucide="${info.icon}" style="width: 14px; height: 14px;"></i>
                <span class="lore-filename">${pageName.replace(/_/g, ' ')}</span>
                <span class="lore-count" style="font-size: 0.8em; color: var(--secondary-text);">${info.display}</span>
            `;

            const editBtn = document.createElement('button');
            editBtn.className = 'top-bar-btn';
            editBtn.style.padding = '4px 8px';
            editBtn.style.fontSize = '0.8em';
            editBtn.style.marginLeft = '8px';
            editBtn.innerHTML = '<i data-lucide="edit-2" style="width: 12px; height: 12px;"></i>';
            editBtn.onclick = (e) => {
                e.stopPropagation();
                openPageEditor(category, pageName);
            };

            loreItem.appendChild(headerDiv);
            loreItem.appendChild(editBtn);
            loreList.appendChild(loreItem);
        });
    }

    // Show the "New Page" button
    const createPageBtn = document.getElementById('createPageBtn');
    if (createPageBtn) {
        createPageBtn.style.display = 'flex';
    }

    // Reinitialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// View wiki page details
async function viewLoreFile(filename) {
    if (!currentWiki) {
        alert('No wiki loaded. Please load a wiki first.');
        return;
    }

    const detailCard = document.getElementById('loreDetailCard');
    const detailTitle = document.getElementById('loreDetailTitle');
    const detailContent = document.getElementById('loreDetailContent');

    // Parse filename to get category and page name
    // Format: "Category/Page_Name.md"
    const parts = filename.split('/');
    let category, pageName;

    if (parts.length === 2) {
        category = parts[0].toLowerCase();
        pageName = parts[1].replace('.md', '');
    } else {
        // Fallback: try to detect category from filename
        pageName = filename.replace('.md', '');
        category = 'characters'; // Default to characters
    }

    try {
        const response = await fetch(`${API_URL}/wiki/${currentWiki}/page/${category}/${pageName}`);
        const data = await response.json();

        if (data.success) {
            detailTitle.textContent = pageName.replace(/_/g, ' ');
            detailContent.textContent = data.content;
            detailCard.style.display = 'block';

            // Scroll to detail card
            detailCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } else {
            alert(`Failed to load page: ${data.detail || 'Page not found'}`);
        }
    } catch (error) {
        console.error('Error loading wiki page:', error);
        alert(`Error: ${error.message}`);
    }

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

// ============================================================================
// Session Browser
// ============================================================================

async function openSessionBrowser() {
    if (!currentWiki) {
        alert('No wiki loaded. Please load a wiki first.');
        return;
    }

    const modal = document.getElementById('sessionBrowserModal');
    const sessionList = document.getElementById('sessionList');
    const sessionEmptyState = document.getElementById('sessionEmptyState');

    try {
        const response = await fetch(`${API_URL}/wiki/${currentWiki}`);
        const data = await response.json();

        if (data.success) {
            const wikiNameSpan = document.getElementById('sessionBrowserWikiName');
            const sessionCountSpan = document.getElementById('sessionBrowserSessionCount');

            wikiNameSpan.textContent = data.metadata.name;
            sessionCountSpan.textContent = `${data.sessions.length} session(s)`;

            if (data.sessions.length === 0) {
                sessionList.innerHTML = '';
                sessionEmptyState.style.display = 'block';
            } else {
                sessionEmptyState.style.display = 'none';
                populateSessionList(data.sessions);
            }

            modal.classList.add('active');
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        }
    } catch (error) {
        console.error('Error loading sessions:', error);
        alert(`Error: ${error.message}`);
    }
}

function populateSessionList(sessions) {
    const sessionList = document.getElementById('sessionList');
    sessionList.innerHTML = '';

    sessions.forEach((session, index) => {
        const sessionItem = document.createElement('div');
        sessionItem.className = 'wiki-item';
        sessionItem.style.marginBottom = '12px';

        const savedDate = new Date(session.saved);
        const formattedDate = savedDate.toLocaleString();

        sessionItem.innerHTML = `
            <div class="wiki-item-icon">
                <i data-lucide="message-square" style="width: 24px; height: 24px;"></i>
            </div>
            <div class="wiki-item-info">
                <div class="wiki-item-name">Session ${index + 1}</div>
                <div class="wiki-item-meta">${session.message_count} messages • ${formattedDate}</div>
            </div>
            <div class="wiki-item-actions">
                <button class="top-bar-btn" style="padding: 6px 12px; font-size: 0.85em;" onclick="loadSession('${session.session_id}')">
                    <i data-lucide="download" style="width: 14px; height: 14px;"></i>
                    Load
                </button>
            </div>
        `;

        sessionList.appendChild(sessionItem);
    });

    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

async function loadSession(session_id) {
    if (!currentWiki) {
        alert('No wiki loaded.');
        return;
    }

    // Warn if current chat has messages
    const chatContainer = document.getElementById('chatContainer');
    const messages = chatContainer.querySelectorAll('.message:not(.welcome-message)');

    if (messages.length > 0) {
        if (!confirm('Loading a session will replace your current conversation. Continue?')) {
            return;
        }
    }

    try {
        const response = await fetch(`${API_URL}/wiki/${currentWiki}/session/${session_id}`);
        const data = await response.json();

        if (data.success) {
            // Clear current chat
            messages.forEach(msg => msg.remove());

            // Load session messages
            data.conversation.forEach(msg => {
                addMessage(msg.content, msg.role === 'user', msg.lore_used || []);
            });

            // Update session ID
            sessionId = session_id;

            // Close modal
            closeSessionBrowserModal();

            alert(`Loaded session with ${data.conversation.length} messages`);
        } else {
            alert('Failed to load session');
        }
    } catch (error) {
        console.error('Error loading session:', error);
        alert(`Error: ${error.message}`);
    }
}

function closeSessionBrowserModal() {
    const modal = document.getElementById('sessionBrowserModal');
    modal.classList.remove('active');
}

// ============================================================================
// Wiki Page Editor
// ============================================================================

let editingPage = null; // Track which page is being edited

function openPageEditor(category = null, pageName = null) {
    if (!currentWiki) {
        alert('No wiki loaded. Please load a wiki first.');
        return;
    }

    const modal = document.getElementById('pageEditorModal');
    const titleSpan = document.getElementById('pageEditorTitle');
    const nameInput = document.getElementById('pageNameInput');
    const categorySelect = document.getElementById('pageCategorySelect');
    const contentEditor = document.getElementById('pageContentEditor');
    const deleteBtn = document.getElementById('deletePageBtn');

    // Reset form
    nameInput.value = '';
    contentEditor.value = '';

    if (category && pageName) {
        // Edit existing page
        titleSpan.textContent = 'Edit Page';
        nameInput.value = pageName.replace(/_/g, ' ');
        categorySelect.value = category;
        deleteBtn.style.display = 'block';
        editingPage = { category, pageName };

        // Load page content
        loadPageContent(category, pageName);
    } else {
        // Create new page
        titleSpan.textContent = 'Create New Page';
        categorySelect.value = 'characters';
        deleteBtn.style.display = 'none';
        editingPage = null;
    }

    modal.classList.add('active');
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

async function loadPageContent(category, pageName) {
    try {
        const response = await fetch(`${API_URL}/wiki/${currentWiki}/page/${category}/${pageName}`);
        const data = await response.json();

        if (data.success) {
            document.getElementById('pageContentEditor').value = data.content;
        }
    } catch (error) {
        console.error('Error loading page content:', error);
    }
}

async function savePage() {
    if (!currentWiki) {
        alert('No wiki loaded.');
        return;
    }

    const nameInput = document.getElementById('pageNameInput');
    const categorySelect = document.getElementById('pageCategorySelect');
    const contentEditor = document.getElementById('pageContentEditor');

    const pageName = nameInput.value.trim();
    const category = categorySelect.value;
    const content = contentEditor.value;

    if (!pageName) {
        alert('Please enter a page name.');
        return;
    }

    if (!content) {
        alert('Please enter some content.');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/wiki/${currentWiki}/page/${category}/${pageName}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: content
            })
        });

        const data = await response.json();

        if (data.success) {
            alert('Page saved successfully!');
            closePageEditorModal();

            // Reload wiki to refresh page list
            const wikiResponse = await fetch(`${API_URL}/wiki/${currentWiki}`);
            const wikiData = await wikiResponse.json();
            if (wikiData.success) {
                loadWikiPages(wikiData.pages);
            }
        } else {
            alert(`Failed to save page: ${data.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error saving page:', error);
        alert(`Error: ${error.message}`);
    }
}

async function deletePage() {
    if (!editingPage) {
        return;
    }

    if (!confirm(`Are you sure you want to delete this page? This cannot be undone.`)) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/wiki/${currentWiki}/page/${editingPage.category}/${editingPage.pageName}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            alert('Page deleted successfully!');
            closePageEditorModal();

            // Reload wiki to refresh page list
            const wikiResponse = await fetch(`${API_URL}/wiki/${currentWiki}`);
            const wikiData = await wikiResponse.json();
            if (wikiData.success) {
                loadWikiPages(wikiData.pages);
            }
        } else {
            alert(`Failed to delete page: ${data.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error deleting page:', error);
        alert(`Error: ${error.message}`);
    }
}

function closePageEditorModal() {
    const modal = document.getElementById('pageEditorModal');
    modal.classList.remove('active');
    editingPage = null;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Get all elements
    const openWikiBtn = document.getElementById('openWikiBtn');
    const saveWikiBtn = document.getElementById('saveWikiBtn');
    const autoSyncToggle = document.getElementById('autoSyncToggle');
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

    // Auto-sync toggle
    if (autoSyncToggle) {
        autoSyncToggle.addEventListener('click', toggleAutoSync);
    }

    // Page editor buttons
    const createPageBtn = document.getElementById('createPageBtn');
    const savePageBtn = document.getElementById('savePageBtn');
    const deletePageBtn = document.getElementById('deletePageBtn');

    if (createPageBtn) {
        createPageBtn.addEventListener('click', () => openPageEditor());
    }

    if (savePageBtn) {
        savePageBtn.addEventListener('click', savePage);
    }

    if (deletePageBtn) {
        deletePageBtn.addEventListener('click', deletePage);
    }

    // Close buttons (X icons) - use event delegation for Lucide icon replacement
    document.addEventListener('click', (e) => {
        const closeWikiBrowserBtn = e.target.closest('#closeWikiBrowserModal');
        if (closeWikiBrowserBtn) {
            e.stopPropagation();
            closeWikiBrowserModal();
        }

        const closeSaveWikiBtn = e.target.closest('#closeSaveWikiModal');
        if (closeSaveWikiBtn) {
            e.stopPropagation();
            closeSaveWikiModal();
        }

        const closeSessionBrowserBtn = e.target.closest('#closeSessionBrowserModal');
        if (closeSessionBrowserBtn) {
            e.stopPropagation();
            closeSessionBrowserModal();
        }

        const closePageEditorBtn = e.target.closest('#closePageEditorModal');
        if (closePageEditorBtn) {
            e.stopPropagation();
            closePageEditorModal();
        }

        const closeNotificationsBtn = e.target.closest('#closeNotificationsModal');
        if (closeNotificationsBtn) {
            e.stopPropagation();
            closeNotificationsModal();
        }

        const closeProfileBtn = e.target.closest('#closeProfileModal');
        if (closeProfileBtn) {
            e.stopPropagation();
            closeProfileModal();
        }
    });

    // Top bar icons - use event delegation to handle Lucide icon replacement
    document.addEventListener('click', (e) => {
        const notifIcon = e.target.closest('#notificationsIcon');
        if (notifIcon) {
            e.stopPropagation();
            openNotificationsModal();
        }

        const profIcon = e.target.closest('#profileIcon');
        if (profIcon) {
            e.stopPropagation();
            openProfileModal();
        }
    });

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

/* ============================================================================
   DOAMMO UI - Chat Functionality
   ============================================================================ */

let sessionId = null;

function addMessage(content, isUser, loreUsed = []) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'ai'}`;

    let messageHTML = `
        <div class="message-content">
            <div class="message-text">${escapeHtml(content)}</div>`;

    // Add lore tags if present
    if (loreUsed && loreUsed.length > 0) {
        messageHTML += `<div class="lore-tags">Lore used: `;
        loreUsed.forEach(lore => {
            messageHTML += `<span class="lore-tag">${escapeHtml(lore)}</span>`;
        });
        messageHTML += `</div>`;
    }

    // Add edit button (enabled)
    messageHTML += `
            <div class="message-actions">
                <button class="message-action-btn" title="Edit Message">
                    <i data-lucide="edit-2" style="width: 14px; height: 14px;"></i>
                    Edit
                </button>
            </div>
        </div>`;

    messageDiv.innerHTML = messageHTML;

    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Track message count for controls
    if (typeof messageCount !== 'undefined') {
        messageCount++;
        if (typeof updateControlStates === 'function') {
            updateControlStates();
        }
    }

    // Reinitialize icons for new content
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function showLoading() {
    const chatContainer = document.getElementById('chatContainer');
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loadingIndicator';
    loadingDiv.className = 'loading';
    loadingDiv.textContent = 'Generating narrative';
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function hideLoading() {
    const loading = document.getElementById('loadingIndicator');
    if (loading) {
        loading.remove();
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function sendMessage() {
    const input = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const message = input.value.trim();

    if (!message) return;

    // Disable input
    input.disabled = true;
    sendBtn.disabled = true;

    // Add user message
    addMessage(message, true);
    input.value = '';

    // Show loading
    showLoading();

    try {
        const response = await fetch(`${API_URL}/narrative`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_input: message,
                session_id: sessionId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Update session ID if this is the first message
        if (!sessionId) {
            sessionId = data.session_id;
        }

        // Hide loading and add AI response
        hideLoading();
        addMessage(data.narrative, false, data.lore_used);

        // Auto-save to wiki if enabled
        if (typeof autoSaveToWiki === 'function') {
            await autoSaveToWiki();
        }

        // Lore Keeper - extract lore from narrative if enabled
        if (typeof extractLoreFromNarrative === 'function') {
            extractLoreFromNarrative(data.narrative);
        }

    } catch (error) {
        hideLoading();
        showError(error, message);
        console.error('Error sending message:', error);
    } finally {
        // Re-enable input
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }
}

/* ============================================================================
   Error Handling
   ============================================================================ */

function showError(error, originalMessage = null) {
    const chatContainer = document.getElementById('chatContainer');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message error';

    let errorMessage = 'An error occurred';
    let errorDetails = '';
    let showRetry = false;

    // Categorize error types
    if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        errorMessage = 'Connection Error';
        errorDetails = `Cannot reach the API server at ${API_URL}. Make sure the server is running.`;
        showRetry = true;
    } else if (error.message.includes('HTTP error! status: 401')) {
        errorMessage = 'Authentication Error';
        errorDetails = 'Invalid API key. Check your .env file and restart the server.';
    } else if (error.message.includes('HTTP error! status: 429')) {
        errorMessage = 'Rate Limit Exceeded';
        errorDetails = 'Too many requests. Please wait a moment and try again.';
        showRetry = true;
    } else if (error.message.includes('HTTP error! status: 500')) {
        errorMessage = 'Server Error';
        errorDetails = 'The server encountered an error. Check the server logs for details.';
        showRetry = true;
    } else if (error.message.includes('HTTP error!')) {
        errorMessage = 'API Error';
        errorDetails = `Server returned error: ${error.message}`;
    } else {
        errorMessage = 'Unexpected Error';
        errorDetails = error.message;
    }

    let errorHTML = `
        <div class="message-content">
            <div class="error-icon">⚠️</div>
            <div class="error-text">
                <strong>${errorMessage}</strong>
                <p>${errorDetails}</p>
            </div>`;

    if (showRetry && originalMessage) {
        errorHTML += `
            <div class="message-actions">
                <button class="retry-btn" onclick="retryMessage('${escapeHtml(originalMessage)}')">
                    <i data-lucide="refresh-cw" style="width: 14px; height: 14px;"></i>
                    Retry
                </button>
            </div>`;
    }

    errorHTML += `</div>`;
    errorDiv.innerHTML = errorHTML;

    chatContainer.appendChild(errorDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Reinitialize icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

async function retryMessage(message) {
    const input = document.getElementById('userInput');
    input.value = message;
    await sendMessage();
}

/* ============================================================================
   Export Functionality
   ============================================================================ */

function exportChatToMarkdown() {
    const messages = document.querySelectorAll('.message:not(.error):not(.loading)');
    let markdown = `# DOAMMO Session Export\n\n`;
    markdown += `**Exported:** ${new Date().toLocaleString()}\n`;
    markdown += `**Session ID:** ${sessionId || 'No session'}\n\n`;
    markdown += `---\n\n`;

    messages.forEach((msg, index) => {
        const isUser = msg.classList.contains('user');
        const content = msg.querySelector('.message-text')?.textContent || '';
        const loreTagsEl = msg.querySelector('.lore-tags');

        if (isUser) {
            markdown += `## Turn ${Math.floor(index / 2) + 1} - Player\n\n`;
            markdown += `${content}\n\n`;
        } else {
            markdown += `## AI Response\n\n`;
            markdown += `${content}\n\n`;

            if (loreTagsEl) {
                const loreTags = Array.from(loreTagsEl.querySelectorAll('.lore-tag'))
                    .map(tag => tag.textContent);
                markdown += `*Lore used: ${loreTags.join(', ')}*\n\n`;
            }
        }
    });

    downloadFile(markdown, `doammo-session-${Date.now()}.md`, 'text/markdown');
}

function exportChatToJSON() {
    const messages = document.querySelectorAll('.message:not(.error):not(.loading)');
    const exportData = {
        session_id: sessionId,
        exported_at: new Date().toISOString(),
        messages: []
    };

    messages.forEach(msg => {
        const isUser = msg.classList.contains('user');
        const content = msg.querySelector('.message-text')?.textContent || '';
        const loreTagsEl = msg.querySelector('.lore-tags');
        const loreTags = loreTagsEl ?
            Array.from(loreTagsEl.querySelectorAll('.lore-tag')).map(tag => tag.textContent) :
            [];

        exportData.messages.push({
            role: isUser ? 'user' : 'assistant',
            content: content,
            lore_used: loreTags,
            timestamp: new Date().toISOString()
        });
    });

    const json = JSON.stringify(exportData, null, 2);
    downloadFile(json, `doammo-session-${Date.now()}.json`, 'application/json');
}

function copyToClipboard() {
    const messages = document.querySelectorAll('.message:not(.error):not(.loading)');
    let text = `DOAMMO Session - ${new Date().toLocaleString()}\n\n`;

    messages.forEach(msg => {
        const isUser = msg.classList.contains('user');
        const content = msg.querySelector('.message-text')?.textContent || '';
        text += `${isUser ? 'You' : 'AI'}: ${content}\n\n`;
    });

    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showNotification('Failed to copy to clipboard', 'error');
    });
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    showNotification(`Downloaded ${filename}`);
}

function showNotification(message, type = 'success') {
    // Simple notification - can be enhanced with UI redesign
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        background: ${type === 'error' ? '#ff4444' : '#44ff44'};
        color: #000;
        border-radius: 4px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Auto-focus input on page load
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('userInput').focus();
    initJumpToEndButton();
});

/* ============================================================================
   Jump to End Button
   ============================================================================ */

function initJumpToEndButton() {
    const chatContainer = document.getElementById('chatContainer');
    const jumpBtn = document.getElementById('jumpToEndBtn');

    if (!chatContainer || !jumpBtn) return;

    // Check scroll position and show/hide button
    chatContainer.addEventListener('scroll', () => {
        updateJumpButtonVisibility();
    });

    // Initial check
    updateJumpButtonVisibility();
}

function updateJumpButtonVisibility() {
    const chatContainer = document.getElementById('chatContainer');
    const jumpBtn = document.getElementById('jumpToEndBtn');

    if (!chatContainer || !jumpBtn) return;

    // Calculate if we're near the bottom (within 100px)
    const isNearBottom = chatContainer.scrollHeight - chatContainer.scrollTop - chatContainer.clientHeight < 100;

    jumpBtn.style.display = isNearBottom ? 'none' : 'flex';
}

function jumpToEndOfChat() {
    const chatContainer = document.getElementById('chatContainer');
    if (!chatContainer) return;

    chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: 'smooth'
    });
}

/* ============================================================================
   DOAMMO UI - Chat Functionality
   ============================================================================ */

let sessionId = null;
const API_URL = 'http://localhost:8000';

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
            console.log('Session started:', sessionId);
        }

        // Hide loading and add AI response
        hideLoading();
        addMessage(data.narrative, false, data.lore_used);

    } catch (error) {
        hideLoading();
        addMessage(`Error: ${error.message}. Make sure the API server is running at ${API_URL}`, false);
        console.error('Error sending message:', error);
    } finally {
        // Re-enable input
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }
}

// Auto-focus input on page load
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('userInput').focus();
});

/* ============================================================================
   DOAMMO UI - Story Controls (Undo, Edit, Export)
   ============================================================================ */

// Track which messages have conversation turns (for enabling/disabling undo)
let messageCount = 0;

// Update control button states based on conversation
function updateControlStates() {
    const undoBtn = document.getElementById('undoBtn');
    const exportBtn = document.getElementById('exportBtn');

    // Enable undo if there's at least one exchange (user + AI)
    if (messageCount >= 2) {
        undoBtn.classList.remove('disabled');
    } else {
        undoBtn.classList.add('disabled');
    }

    // Enable export if there's at least one message
    if (messageCount >= 1) {
        exportBtn.classList.remove('disabled');
    } else {
        exportBtn.classList.add('disabled');
    }
}

// Undo last turn (removes last user message + AI response)
async function undoLastTurn() {
    const undoBtn = document.getElementById('undoBtn');

    if (undoBtn.classList.contains('disabled')) {
        return;
    }

    if (!sessionId) {
        alert('No active session to undo');
        return;
    }

    if (!confirm('Undo the last turn? This will remove your last message and the AI\'s response.')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/session/${sessionId}/undo`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            // Remove last 2 messages from UI (user + AI)
            const chatContainer = document.getElementById('chatContainer');
            const messages = chatContainer.querySelectorAll('.message');

            if (messages.length >= 2) {
                // Remove last two messages (AI response, then user message)
                messages[messages.length - 1].remove();
                messages[messages.length - 2].remove();
                messageCount -= 2;
                updateControlStates();
            }
        } else {
            alert('Failed to undo: ' + (data.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error undoing turn:', error);
        alert(`Error: ${error.message}`);
    }
}

// Edit message
function editMessage(messageElement) {
    const messageText = messageElement.querySelector('.message-text');
    const messageContent = messageElement.querySelector('.message-content');
    const currentText = messageText.textContent;

    // Create textarea
    const textarea = document.createElement('textarea');
    textarea.className = 'message-edit-textarea';
    textarea.value = currentText;
    textarea.style.width = '100%';
    textarea.style.minHeight = '80px';
    textarea.style.padding = '8px';
    textarea.style.borderRadius = '8px';
    textarea.style.border = '1px solid var(--input-border)';
    textarea.style.background = 'var(--tab-navigation-background)';
    textarea.style.color = 'var(--main-text)';
    textarea.style.fontFamily = 'inherit';
    textarea.style.fontSize = 'inherit';
    textarea.style.resize = 'vertical';

    // Expand message-content to full width for editing
    messageContent.style.maxWidth = '100%';

    // Replace text with textarea
    messageText.style.display = 'none';
    messageText.parentNode.insertBefore(textarea, messageText);
    textarea.focus();

    // Create save/cancel buttons
    const actions = messageElement.querySelector('.message-actions');
    const originalHTML = actions.innerHTML;

    actions.innerHTML = `
        <button class="message-action-btn" onclick="saveEdit(this)">
            <i data-lucide="check" style="width: 14px; height: 14px;"></i>
            Save
        </button>
        <button class="message-action-btn" onclick="cancelEdit(this)">
            <i data-lucide="x" style="width: 14px; height: 14px;"></i>
            Cancel
        </button>
    `;
    lucide.createIcons();

    // Store original content for cancel
    messageElement.dataset.originalText = currentText;
    messageElement.dataset.originalActions = originalHTML;
}

// Save edited message
async function saveEdit(buttonElement) {
    const messageElement = buttonElement.closest('.message');
    const textarea = messageElement.querySelector('.message-edit-textarea');
    const messageText = messageElement.querySelector('.message-text');
    const newText = textarea.value.trim();

    if (!newText) {
        alert('Message cannot be empty');
        return;
    }

    if (!sessionId) {
        alert('No active session');
        cancelEdit(buttonElement);
        return;
    }

    // Find message index (excluding welcome message)
    const chatContainer = document.getElementById('chatContainer');
    const allMessages = Array.from(chatContainer.querySelectorAll('.message:not(.welcome-message)'));
    const messageIndex = allMessages.indexOf(messageElement);

    if (messageIndex === -1) {
        alert('Could not find message');
        cancelEdit(buttonElement);
        return;
    }

    try {
        const response = await fetch(`${API_URL}/session/${sessionId}/edit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message_index: messageIndex,
                new_content: newText
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            // Update UI
            messageText.textContent = newText;
            textarea.remove();
            messageText.style.display = '';

            // Restore original max-width
            const messageContent = messageElement.querySelector('.message-content');
            messageContent.style.maxWidth = '';

            // Restore action buttons
            const actions = messageElement.querySelector('.message-actions');
            actions.innerHTML = messageElement.dataset.originalActions;
            lucide.createIcons();

            delete messageElement.dataset.originalText;
            delete messageElement.dataset.originalActions;
        } else {
            alert('Failed to save edit: ' + (data.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error saving edit:', error);
        alert(`Error: ${error.message}`);
        cancelEdit(buttonElement);
    }
}

// Cancel edit
function cancelEdit(buttonElement) {
    const messageElement = buttonElement.closest('.message');
    const textarea = messageElement.querySelector('.message-edit-textarea');
    const messageText = messageElement.querySelector('.message-text');
    const messageContent = messageElement.querySelector('.message-content');

    // Restore original text
    textarea.remove();
    messageText.style.display = '';

    // Restore original max-width
    messageContent.style.maxWidth = '';

    // Restore action buttons
    const actions = messageElement.querySelector('.message-actions');
    actions.innerHTML = messageElement.dataset.originalActions;
    lucide.createIcons();

    delete messageElement.dataset.originalText;
    delete messageElement.dataset.originalActions;
}

// Export story
async function exportStory() {
    const exportBtn = document.getElementById('exportBtn');

    if (exportBtn.classList.contains('disabled')) {
        return;
    }

    if (!sessionId) {
        alert('No active session to export');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/session/${sessionId}/export`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `DOAMMO_Story_${sessionId}.txt`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error('Error exporting story:', error);
        alert(`Error exporting story: ${error.message}`);
    }
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const undoBtn = document.getElementById('undoBtn');
        const exportBtn = document.getElementById('exportBtn');

        if (undoBtn) {
            undoBtn.addEventListener('click', undoLastTurn);
        }

        if (exportBtn) {
            exportBtn.addEventListener('click', exportStory);
        }

        // Enable edit buttons on messages
        document.addEventListener('click', (e) => {
            const editBtn = e.target.closest('.message-action-btn:not(.disabled)');
            if (editBtn && editBtn.textContent.includes('Edit')) {
                const message = editBtn.closest('.message');
                // Ignore welcome message (it's not part of the conversation)
                if (message && !message.classList.contains('welcome-message')) {
                    editMessage(message);
                }
            }
        });
    }, 100);
});

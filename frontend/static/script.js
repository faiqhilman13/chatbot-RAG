document.addEventListener('DOMContentLoaded', () => {
    loadDocuments(); // Load documents when the page loads
    setupEventListeners();
});

function setupEventListeners() {
    const uploadForm = document.getElementById('uploadForm');
    const questionTextarea = document.getElementById('question');
    const askButton = document.getElementById('askButton');

    if (uploadForm) {
        uploadForm.onsubmit = handleUpload;
    }

    if (questionTextarea) {
        // Allow Shift+Enter for new line, Enter to submit
        questionTextarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault(); // Prevent default Enter behavior (new line)
                askQuestion();
            }
        });
    }
    
    // Keep ask button listener as well for click interaction
    if(askButton) {
        askButton.onclick = askQuestion;
    }
}

// --- UI Update Functions ---

function displayMessage(containerId, message, type = 'info') {
    const container = document.getElementById(containerId);
    if (container) {
        container.textContent = message;
        container.className = `status ${type}`;
    }
}

function clearStatus(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.textContent = '';
        container.className = 'status';
    }
}

function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

function addChatMessage(sender, message, sources = null) {
    const chatContainer = document.getElementById('chatContainer');
    if (!chatContainer) return;

    const messageDiv = document.createElement('div');
    messageDiv.classList.add('chat-message');

    if (sender === 'user') {
        messageDiv.classList.add('chat-question');
        messageDiv.textContent = message;
    } else { // sender === 'bot'
        messageDiv.classList.add('chat-answer');
        // Use <pre> for potentially formatted bot answers
        const preFormatted = document.createElement('pre');
        preFormatted.textContent = message;
        messageDiv.appendChild(preFormatted);

        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.classList.add('sources');
            sourcesDiv.innerHTML = '<strong>Sources:</strong><br>' + 
                sources.map(s => `- ${escapeHtml(s.title || s.source || 'Unknown Source')} (Page ${s.page || 'N/A'})`).join('<br>');
            messageDiv.appendChild(sourcesDiv);
        }
    }

    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight; // Auto-scroll to bottom
}

// --- API Interaction Functions ---

async function handleUpload(event) {
    event.preventDefault();
    const fileInput = document.getElementById('fileUpload');
    const titleInput = document.getElementById('docTitle');
    const uploadStatus = document.getElementById('uploadStatus');

    if (!fileInput.files || fileInput.files.length === 0) {
        displayMessage('uploadStatus', 'Please select a PDF file.', 'error');
        return;
    }

    const file = fileInput.files[0];
    const title = titleInput.value.trim() || file.name; // Use filename if title is empty

    if (!file.name.toLowerCase().endsWith('.pdf')) {
        displayMessage('uploadStatus', 'Only PDF files are supported.', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);

    displayMessage('uploadStatus', 'Uploading and processing document...', 'loading');

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || `Upload failed with status ${response.status}`);
        }

        console.log('Upload response:', result);
        displayMessage('uploadStatus', `Document '${escapeHtml(result.title)}' uploaded successfully (ID: ${result.doc_id})`, 'success');
        
        // Clear form fields
        fileInput.value = '';
        titleInput.value = '';
        
        loadDocuments(); // Refresh document list after successful upload

    } catch (error) {
        console.error('Upload error:', error);
        displayMessage('uploadStatus', `Error: ${error.message}`, 'error');
    }
}

async function loadDocuments() {
    const documentList = document.getElementById('documentList');
    if (!documentList) return;
    
    documentList.innerHTML = '<div class="loading">Loading documents...</div>';

    try {
        const response = await fetch('/documents');
        if (!response.ok) {
             const errorData = await response.json().catch(() => ({ detail: 'Failed to fetch documents.' }));
             throw new Error(errorData.detail || `HTTP error ${response.status}`);
        }
        const result = await response.json();
        
        if (result.documents && result.documents.length > 0) {
            documentList.innerHTML = ''; // Clear loading message
            result.documents.forEach(doc => {
                const card = document.createElement('div');
                card.className = 'document-card';
                card.innerHTML = `
                    <div class="document-info">
                        <div class="document-title">${escapeHtml(doc.title)}</div>
                        Filename: ${escapeHtml(doc.filename)} <br>
                        ID: ${escapeHtml(doc.id)}
                    </div>
                    <button class="delete-btn" onclick="deleteDocument('${doc.id}', this)">Delete</button>
                `;
                documentList.appendChild(card);
            });
        } else {
            documentList.innerHTML = '<p>No documents uploaded yet.</p>';
        }
    } catch (error) {
        console.error('Error loading documents:', error);
        documentList.innerHTML = `<p style="color: red;">Error loading documents: ${error.message}</p>`;
    }
}

async function deleteDocument(docId, buttonElement) {
    if (!confirm(`Are you sure you want to delete document ID: ${docId}?`)) {
        return;
    }

    // Visually indicate deletion is in progress
    const originalButtonText = buttonElement.textContent;
    buttonElement.textContent = 'Deleting...';
    buttonElement.disabled = true;

    try {
        const response = await fetch(`/documents/${docId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (!response.ok) {
             throw new Error(result.detail || `Failed to delete with status ${response.status}`);
        }

        console.log('Delete response:', result);
        
        // Remove the document card from the UI
        const card = buttonElement.closest('.document-card');
        if (card) {
            card.remove();
        }
        
        // Optional: Show success message elsewhere if needed
        // displayMessage('someStatusElement', `Document ${docId} deleted.`, 'success');

        // Check if the list is now empty
        const documentList = document.getElementById('documentList');
        if (documentList && !documentList.querySelector('.document-card')) {
             documentList.innerHTML = '<p>No documents uploaded yet.</p>';
        }

    } catch (error) {
        console.error('Delete error:', error);
        alert(`Error deleting document: ${error.message}`);
        // Restore button if deletion failed
        buttonElement.textContent = originalButtonText;
        buttonElement.disabled = false;
    }
}

async function askQuestion() {
    const questionInput = document.getElementById('question');
    const askButton = document.getElementById('askButton');
    const question = questionInput.value.trim();

    if (!question) return;

    // Add user's question to chat UI
    addChatMessage('user', question);

    // Disable input and button during processing
    questionInput.value = ''; // Clear input
    questionInput.disabled = true;
    askButton.disabled = true;
    askButton.textContent = 'Thinking...';

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: question })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || `Error fetching answer (${response.status})`);
        }

        console.log('Ask response:', result);

        // Add bot's answer to chat UI
        addChatMessage('bot', result.answer, result.sources);

    } catch (error) {
        console.error('Ask error:', error);
        addChatMessage('bot', `Sorry, there was an error: ${error.message}`);
    } finally {
        // Re-enable input and button
        questionInput.disabled = false;
        askButton.disabled = false;
        askButton.textContent = 'Ask';
        questionInput.focus(); // Set focus back to the input field
    }
} 
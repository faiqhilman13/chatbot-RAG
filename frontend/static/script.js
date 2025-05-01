document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const apiStatus = document.getElementById('api-status');
    const sourcePanel = document.getElementById('source-panel');
    const closePanel = document.getElementById('close-panel');
    const sourceContent = document.getElementById('source-content');
    const testApiBtn = document.getElementById('test-api-btn');

    // API Configuration
    const API_URL = 'http://localhost:8000';
    const API_ENDPOINTS = {
        health: `${API_URL}/health`,
        ask: `${API_URL}/api/v1/ask`
    };

    // State
    let conversationId = null;
    let isWaitingForResponse = false;

    // Check API status
    checkApiStatus();
    
    // Event Listeners
    chatForm.addEventListener('submit', handleSubmit);
    closePanel.addEventListener('click', toggleSourcePanel);
    testApiBtn.addEventListener('click', testApiConnection);

    // Functions
    function checkApiStatus() {
        const xhr = new XMLHttpRequest();
        xhr.open('GET', API_ENDPOINTS.health, true);
        
        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const data = JSON.parse(xhr.responseText);
                    
                    if (data.status === 'healthy') {
                        apiStatus.textContent = 'Online';
                        apiStatus.classList.add('online');
                    } else {
                        apiStatus.textContent = 'Degraded';
                        apiStatus.classList.add('offline');
                    }
                } catch (error) {
                    apiStatus.textContent = 'Error';
                    apiStatus.classList.add('offline');
                    console.error('API Status parse failed:', error);
                }
            } else {
                apiStatus.textContent = 'Offline';
                apiStatus.classList.add('offline');
                console.error('API Status check failed with status:', xhr.status);
            }
        };
        
        xhr.onerror = function() {
            apiStatus.textContent = 'Offline';
            apiStatus.classList.add('offline');
            console.error('API Status check failed with network error');
        };
        
        xhr.send();
    }

    async function testApiConnection() {
        console.log("Testing API connection directly...");
        const testMessage = "This is a test message";
        
        // Show a system message for the test
        addMessage("Testing API connection...", "system");
        
        // Create a new XMLHttpRequest object
        const xhr = new XMLHttpRequest();
        xhr.open('POST', API_ENDPOINTS.ask, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        
        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const data = JSON.parse(xhr.responseText);
                    console.log('Test response data:', data);
                    addMessage(`API test successful! Response: ${data.answer}`, "system");
                } catch (error) {
                    console.error('Error parsing JSON response:', error);
                    addMessage(`API test succeeded but couldn't parse response: ${xhr.responseText.substring(0, 100)}...`, "system");
                }
            } else {
                console.error('API test error:', xhr.statusText);
                addMessage(`API test failed with status ${xhr.status}: ${xhr.responseText}`, "system");
            }
        };
        
        xhr.onerror = function() {
            console.error('API test network error');
            addMessage("API test failed: Network error - Check browser console and make sure CORS is properly configured", "system");
            
            // Additional troubleshooting information
            addMessage("Troubleshooting steps: 1) Check that backend is running at " + API_URL + 
                      " 2) Check browser console for detailed errors 3) Try direct API call with Python test_api.py", "system");
        };
        
        // Send the request
        xhr.send(JSON.stringify({ question: testMessage }));
    }

    async function handleSubmit(e) {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message || isWaitingForResponse) return;
        
        // Add user message to chat
        addMessage(message, 'user');
        userInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        isWaitingForResponse = true;
        
        try {
            const response = await fetchAnswer(message);
            // Remove typing indicator
            removeTypingIndicator();
            
            // Add bot response
            if (response) {
                addMessage(response.answer, 'bot', response.sources, response.confidence);
            } else {
                addMessage('Sorry, I could not generate a response. Please try again.', 'bot');
            }
        } catch (error) {
            removeTypingIndicator();
            addMessage(`Error: ${error.message}`, 'bot');
            console.error('Error fetching answer:', error);
        }
        
        isWaitingForResponse = false;
    }

    async function fetchAnswer(question) {
        console.log(`Sending request to ${API_ENDPOINTS.ask}`);
        const requestBody = {
            question: question
        };
        
        if (conversationId) {
            requestBody.conversation_id = conversationId;
        }
        
        console.log('Request body:', JSON.stringify(requestBody));
        
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', API_ENDPOINTS.ask, true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            
            xhr.onload = function() {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const data = JSON.parse(xhr.responseText);
                        console.log('Response data:', data);
                        resolve(data);
                    } catch (error) {
                        console.error('Error parsing JSON response:', error);
                        reject(new Error('Failed to parse server response'));
                    }
                } else {
                    console.error('API error response:', xhr.responseText);
                    reject(new Error(`API error (${xhr.status}): ${xhr.responseText}`));
                }
            };
            
            xhr.onerror = function() {
                console.error('Network error occurred');
                reject(new Error('Network error - Failed to reach the server'));
            };
            
            xhr.send(JSON.stringify(requestBody));
        });
    }

    function addMessage(text, sender, sources = [], confidence = null) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        
        const messageText = document.createElement('p');
        messageText.textContent = text;
        contentDiv.appendChild(messageText);
        
        // Add time
        const timeDiv = document.createElement('div');
        timeDiv.classList.add('message-time');
        timeDiv.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        contentDiv.appendChild(timeDiv);
        
        // Add confidence if provided
        if (confidence !== null && sender === 'bot') {
            const confidenceText = document.createElement('div');
            confidenceText.classList.add('message-confidence');
            confidenceText.textContent = `Confidence: ${Math.round(confidence * 100)}%`;
            contentDiv.appendChild(confidenceText);
        }
        
        // Add sources if provided and not empty
        if (sources && sources.length > 0 && sender === 'bot') {
            const sourcesLink = document.createElement('div');
            sourcesLink.classList.add('message-sources');
            sourcesLink.textContent = `Sources (${sources.length})`;
            sourcesLink.addEventListener('click', () => {
                displaySources(sources);
                toggleSourcePanel(true);
            });
            contentDiv.appendChild(sourcesLink);
        }
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to the bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('message', 'bot', 'typing-indicator-container');
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator-container');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    function displaySources(sources) {
        // Clear previous sources
        sourceContent.innerHTML = '';
        
        if (sources.length === 0) {
            const noSources = document.createElement('p');
            noSources.textContent = 'No sources available.';
            sourceContent.appendChild(noSources);
            return;
        }
        
        // Add sources to panel
        sources.forEach((source, index) => {
            const sourceDiv = document.createElement('div');
            sourceDiv.classList.add('source-item');
            
            const sourceName = document.createElement('div');
            sourceName.classList.add('source-name');
            sourceName.textContent = `Source ${index + 1}`;
            
            const sourceText = document.createElement('div');
            sourceText.classList.add('source-text');
            sourceText.textContent = source;
            
            sourceDiv.appendChild(sourceName);
            sourceDiv.appendChild(sourceText);
            sourceContent.appendChild(sourceDiv);
        });
    }

    function toggleSourcePanel(show) {
        if (show === true) {
            sourcePanel.classList.add('active');
        } else if (show === false) {
            sourcePanel.classList.remove('active');
        } else {
            sourcePanel.classList.toggle('active');
        }
    }
}); 
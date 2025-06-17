import React, { useState, useRef, useEffect } from 'react';
import './ChatSection.css';

const ChatSection = () => {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatContainerRef = useRef(null);

  // Scroll to bottom of chat container when messages change
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const escapeHtml = (unsafe) => {
    if (!unsafe) return '';
    return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  };

  const handleQuestionChange = (e) => {
    setQuestion(e.target.value);
  };

  const handleKeyDown = (e) => {
    // Allow Shift+Enter for new line, Enter to submit
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = async () => {
    if (!question.trim()) return;

    // Add user's question to chat
    const userMessage = {
      type: 'user',
      content: question.trim(),
    };
    setMessages([...messages, userMessage]);
    
    // Clear input and set loading state
    setQuestion('');
    setIsLoading(true);

    try {
      const response = await fetch('/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: question.trim() })
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || `Error fetching answer (${response.status})`);
      }

      // Add bot's answer to chat
      const botMessage = {
        type: 'bot',
        content: result.answer,
        sources: result.sources || []
      };
      setMessages(messages => [...messages, botMessage]);
    } catch (error) {
      console.error('Ask error:', error);
      const errorMessage = {
        type: 'bot',
        content: `Sorry, there was an error: ${error.message}`,
        error: true
      };
      setMessages(messages => [...messages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="section chat-section">
      <h2>Chat</h2>
      <div className="chat-container" ref={chatContainerRef}>
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`chat-message ${message.type === 'user' ? 'chat-question' : 'chat-answer'}`}
          >
            {message.type === 'user' ? (
              message.content
            ) : (
              <>
                <pre>{message.content}</pre>
                {message.sources && message.sources.length > 0 && (
                  <div className="sources">
                    <strong>Sources:</strong><br />
                    {message.sources.map((source, idx) => (
                      <div key={idx}>
                        - {escapeHtml(source.title || source.source || 'Unknown Source')} (Page {source.page || 'N/A'})
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        ))}
      </div>
      <div className="chat-input">
        <textarea
          value={question}
          onChange={handleQuestionChange}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about the uploaded documents..."
          disabled={isLoading}
        />
        <button 
          onClick={handleSubmit} 
          disabled={isLoading || !question.trim()}
        >
          {isLoading ? 'Thinking...' : 'Ask'}
        </button>
      </div>
    </div>
  );
};

export default ChatSection; 
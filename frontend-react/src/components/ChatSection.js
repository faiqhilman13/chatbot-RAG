import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../context/ChatContext';
import './ChatSection.css';

const ChatSection = ({ className }) => {
  const [question, setQuestion] = useState('');
  const [documentFilter, setDocumentFilter] = useState(null);
  const [showFilters, setShowFilters] = useState(false);
  const chatContainerRef = useRef(null);
  const { 
    activeChat, 
    addMessage, 
    isLoading, 
    setIsLoading, 
    createNewChat 
  } = useChat();

  // Get messages from active chat or empty array if no active chat
  const messages = activeChat ? activeChat.messages : [];

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

  // Function to format AI responses with basic markdown-like formatting
  const formatAIResponse = (text) => {
    if (!text) return '';
    
    // Replace line breaks with <br> tags
    let formatted = text.replace(/\n/g, '<br>');
    
    // Format headings (# Heading)
    formatted = formatted.replace(/(?:<br>|^)#\s+(.*?)(?:<br>|$)/g, '<h2>$1</h2>');
    
    // Format bold text (**text**)
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Format italic text (*text*)
    formatted = formatted.replace(/\*([^*<>]+)\*/g, '<em>$1</em>');
    
    // Format inline code (`code`)
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Format bullet points
    formatted = formatted.replace(/(?:<br>|^)\s*-\s+(.*?)(?:<br>|$)/g, '<br>• $1<br>');
    
    return formatted;
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
  
  const toggleFilters = () => {
    setShowFilters(!showFilters);
  };

  const setFilter = (filterType) => {
    if (filterType === 'cv') {
      setDocumentFilter({ title: ["cv", "resume", "faiq cv", "faiq hilman", "faiq hilman cv"] });
    } else if (filterType === 'financial') {
      setDocumentFilter({ title: ["tesla fy24", "financial report", "earnings report"] });
    } else {
      setDocumentFilter(null); // Clear filter
    }
  };

  const handleSubmit = async () => {
    if (!question.trim()) return;

    // Add user's question to chat
    const userMessage = {
      type: 'user',
      content: question.trim(),
      filter: documentFilter // Store the filter used with this question
    };
    addMessage(userMessage);
    
    // Clear input and set loading state
    setQuestion('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/ask', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          question: question.trim(),
          doc_filter: documentFilter // Include document filter if set
        })
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
      addMessage(botMessage);
    } catch (error) {
      console.error('Ask error:', error);
      const errorMessage = {
        type: 'bot',
        content: `Sorry, there was an error: ${error.message}`,
        error: true
      };
      addMessage(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    createNewChat();
  };

  return (
    <div className={`chat-section ${className || ''}`}>
      <div className="chat-container" ref={chatContainerRef}>
        {messages.length === 0 && (
          <div className="empty-chat-message">
            Your conversation will appear here. Ask a question about your documents to get started.
          </div>
        )}
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`chat-message ${message.type === 'user' ? 'chat-question' : 'chat-answer'}`}
          >
            {message.type === 'user' ? (
              <div>
                {message.content}
                {message.filter && (
                  <div className="filter-tag">
                    {message.filter.title && message.filter.title.includes('cv') ? 'CV/Resume Only' : 
                     message.filter.title && message.filter.title.includes('tesla') ? 'Financial Reports Only' : 
                     'Filtered'}
                  </div>
                )}
              </div>
            ) : (
              <>
                <div 
                  className="chat-answer-content"
                  dangerouslySetInnerHTML={{ __html: formatAIResponse(message.content) }}
                />
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
      <div className="chat-input-wrapper">
        {showFilters && (
          <div className="filter-options">
            <button 
              className={`filter-btn ${documentFilter && documentFilter.title && documentFilter.title.includes('cv') ? 'active' : ''}`}
              onClick={() => setFilter('cv')}
            >
              CV/Resume Only
            </button>
            <button 
              className={`filter-btn ${documentFilter && documentFilter.title && documentFilter.title.includes('tesla') ? 'active' : ''}`}
              onClick={() => setFilter('financial')}
            >
              Financial Reports Only
            </button>
            <button 
              className={`filter-btn ${!documentFilter ? 'active' : ''}`}
              onClick={() => setFilter(null)}
            >
              All Documents
            </button>
          </div>
        )}
        
        <div className="chat-input">
          <textarea
            value={question}
            onChange={handleQuestionChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything..."
            disabled={isLoading}
          />
          <div className="chat-input-buttons">
            <button 
              className="filter-toggle"
              onClick={toggleFilters}
              title="Toggle document filters"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
              </svg>
            </button>
            <button 
              onClick={handleSubmit} 
              disabled={isLoading || !question.trim()}
            >
              {isLoading ? 'Thinking...' : 'Ask'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatSection; 
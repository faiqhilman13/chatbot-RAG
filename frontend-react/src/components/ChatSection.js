import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../context/ChatContext';
import './ChatSection.css';

const ChatSection = ({ className }) => {
  const [question, setQuestion] = useState('');
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

  const handleSubmit = async () => {
    if (!question.trim()) return;

    // Add user's question to chat
    const userMessage = {
      type: 'user',
      content: question.trim(),
    };
    addMessage(userMessage);
    
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
              <div>{message.content}</div>
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
      <div className="chat-input">
        <textarea
          value={question}
          onChange={handleQuestionChange}
          onKeyDown={handleKeyDown}
          placeholder="Ask me anything..."
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
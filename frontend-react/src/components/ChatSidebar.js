import React from 'react';
import { useChat } from '../context/ChatContext';
import './ChatSidebar.css';

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  });
};

const ChatSidebar = () => {
  const { 
    chatHistory, 
    activeChatId, 
    setActiveChatId, 
    createNewChat, 
    deleteChat 
  } = useChat();

  const handleChatClick = (chatId) => {
    setActiveChatId(chatId);
  };

  const handleNewChat = () => {
    createNewChat();
  };

  const handleDeleteChat = (e, chatId) => {
    e.stopPropagation(); // Prevent triggering the parent onClick
    if (window.confirm('Are you sure you want to delete this chat?')) {
      deleteChat(chatId);
    }
  };

  return (
    <div className="chat-sidebar">
      <div className="chat-sidebar-header">
        <div className="chat-sidebar-title">Chat History</div>
      </div>
      
      <button className="new-chat-btn" onClick={handleNewChat}>
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        New Chat
      </button>
      
      <div className="chat-sidebar-list">
        {chatHistory.length === 0 ? (
          <div className="empty-history">No chat history yet</div>
        ) : (
          chatHistory.map(chat => (
            <div 
              key={chat.id}
              className={`chat-item ${chat.id === activeChatId ? 'active' : ''}`}
              onClick={() => handleChatClick(chat.id)}
            >
              <div className="chat-item-content">
                <div className="chat-item-title">{chat.title}</div>
                <div className="chat-item-date">{formatDate(chat.updatedAt)}</div>
              </div>
              <div className="chat-item-actions">
                <button 
                  className="chat-item-delete"
                  onClick={(e) => handleDeleteChat(e, chat.id)}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                  </svg>
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ChatSidebar; 
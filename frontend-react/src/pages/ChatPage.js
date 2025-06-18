import React from 'react';
import ChatSection from '../components/ChatSection';
import ChatSidebar from '../components/ChatSidebar';
import Logo from '../components/Logo';
import './ChatPage.css';
import { useChat } from '../context/ChatContext';

const ChatPage = () => {
  const { activeChat } = useChat();

  return (
    <>
      <ChatSidebar />
      <div className="chat-page with-sidebar">
        <div className="chat-page-header">
          <Logo />
          <h1>Hi there</h1>
          <p className="welcome-text">
            {activeChat ? `Continuing chat: ${activeChat.title}` : 'Start a new conversation or select a chat from the sidebar'}
          </p>
        </div>
        <ChatSection className="chat-card" />
      </div>
    </>
  );
};

export default ChatPage; 
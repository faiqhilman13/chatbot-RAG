import React from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import ParticleBackground from './components/ParticleBackground';
import { PageProvider, usePage, PAGES } from './context/PageContext';
import { ChatProvider } from './context/ChatContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { StagewiseToolbar } from '@stagewise/toolbar-react';
import { ReactPlugin } from '@stagewise-plugins/react';

// Import pages
import ChatPage from './pages/ChatPage';
import DocumentsPage from './pages/DocumentsPage';
import UploadPage from './pages/UploadPage';
import MonitoringPage from './pages/MonitoringPage';
import FeedbackPage from './pages/FeedbackPage';
import LoginPage from './pages/LoginPage';

// Main content component that renders the active page
const MainContent = () => {
  const { activePage } = usePage();

  const renderActivePage = () => {
    switch (activePage) {
      case PAGES.CHAT:
        return <ChatPage />;
      case PAGES.DOCUMENTS:
        return <DocumentsPage />;
      case PAGES.UPLOAD:
        return <UploadPage />;
      case PAGES.MONITORING:
        return <MonitoringPage />;
      case PAGES.FEEDBACK:
        return <FeedbackPage />;
      default:
        return <ChatPage />;
    }
  };

  // Add the with-chat-sidebar class when on the chat page
  const contentClass = activePage === PAGES.CHAT 
    ? "main-content-wrapper with-chat-sidebar" 
    : "main-content-wrapper";

  return (
    <div className={contentClass}>
      <div className="main-content">
        {renderActivePage()}
      </div>
    </div>
  );
};

// Component that handles auth state
const AppContent = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="loading-screen">
        <ParticleBackground />
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <>
        <ParticleBackground />
        <LoginPage />
      </>
    );
  }

  return (
    <PageProvider>
      <ChatProvider>
        <div className="App">
          <ParticleBackground />
          <Sidebar />
          <MainContent />
        </div>
      </ChatProvider>
    </PageProvider>
  );
};

function App() {
  return (
    <AuthProvider>
      <StagewiseToolbar 
        config={{
          plugins: [ReactPlugin]
        }}
      />
      <AppContent />
    </AuthProvider>
  );
}

export default App; 
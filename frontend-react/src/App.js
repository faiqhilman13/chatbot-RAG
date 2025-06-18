import React from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import { StagewiseToolbar } from '@stagewise/toolbar-react';
import { ReactPlugin } from '@stagewise-plugins/react';
import { PageProvider, usePage, PAGES } from './context/PageContext';
import { ChatProvider } from './context/ChatContext';

// Import pages
import ChatPage from './pages/ChatPage';
import DocumentsPage from './pages/DocumentsPage';
import UploadPage from './pages/UploadPage';

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

function App() {
  return (
    <PageProvider>
      <ChatProvider>
        <div className="App">
          <StagewiseToolbar config={{ plugins: [ReactPlugin] }} />
          <Sidebar />
          <MainContent />
        </div>
      </ChatProvider>
    </PageProvider>
  );
}

export default App; 
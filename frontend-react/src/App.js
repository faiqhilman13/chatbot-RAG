import React, { useState, useEffect } from 'react';
import './App.css';
import UploadSection from './components/UploadSection';
import DocumentsSection from './components/DocumentsSection';
import ChatSection from './components/ChatSection';
import { StagewiseToolbar } from '@stagewise/toolbar-react';
import { ReactPlugin } from '@stagewise-plugins/react';

function App() {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load documents when the component mounts
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('/documents');
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to fetch documents.' }));
        throw new Error(errorData.detail || `HTTP error ${response.status}`);
      }
      const result = await response.json();
      setDocuments(result.documents || []);
    } catch (error) {
      console.error('Error loading documents:', error);
      setError(`Error loading documents: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDocumentDelete = async (docId) => {
    // Filter out the deleted document from state
    setDocuments(documents.filter(doc => doc.id !== docId));
  };

  return (
    <div className="App">
      <StagewiseToolbar config={{ plugins: [ReactPlugin] }} />
      <h1>Hybrid RAG Chatbot</h1>
      <div className="container">
        <div className="sidebar">
          <UploadSection onDocumentUploaded={loadDocuments} />
          <DocumentsSection 
            documents={documents} 
            isLoading={isLoading} 
            error={error} 
            onRefresh={loadDocuments}
            onDelete={handleDocumentDelete}
          />
        </div>
        <ChatSection />
      </div>
    </div>
  );
}

export default App; 
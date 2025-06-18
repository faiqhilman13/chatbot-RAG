import React, { useState, useEffect } from 'react';
import DocumentsSection from '../components/DocumentsSection';
import Logo from '../components/Logo';
import './DocumentsPage.css';
import { usePage, PAGES } from '../context/PageContext';

const DocumentsPage = () => {
  const { setActivePage } = usePage();
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

  const handleUploadClick = () => {
    setActivePage(PAGES.UPLOAD);
  };

  return (
    <div className="documents-page">
      <Logo />
      <h1>Document Library</h1>
      <p>
        Manage your uploaded documents or{' '}
        <button className="link-button" onClick={handleUploadClick}>
          upload a new document
        </button>
      </p>
      <DocumentsSection
        className="card"
        documents={documents}
        isLoading={isLoading}
        error={error}
        onRefresh={loadDocuments}
        onDelete={handleDocumentDelete}
      />
    </div>
  );
};

export default DocumentsPage; 
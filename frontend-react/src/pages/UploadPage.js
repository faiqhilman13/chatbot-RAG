import React from 'react';
import UploadSection from '../components/UploadSection';
import Logo from '../components/Logo';
import './UploadPage.css';
import { usePage, PAGES } from '../context/PageContext';

const UploadPage = () => {
  const { setActivePage } = usePage();

  const handleDocumentUploaded = () => {
    // Redirect to documents page after successful upload
    setTimeout(() => {
      setActivePage(PAGES.DOCUMENTS);
    }, 2000); // Give user time to see the success message
  };

  const handleViewDocuments = () => {
    setActivePage(PAGES.DOCUMENTS);
  };

  return (
    <div className="upload-page">
      <Logo />
      <h1>Upload Document</h1>
      <p>
        Upload PDF documents to build the knowledge base or{' '}
        <button className="link-button" onClick={handleViewDocuments}>
          view your existing documents
        </button>
      </p>
      <UploadSection className="card" onDocumentUploaded={handleDocumentUploaded} />
    </div>
  );
};

export default UploadPage; 
import React, { useState } from 'react';
import './DocumentsSection.css';

const DocumentsSection = ({ className, documents, isLoading, error, onRefresh, onDelete }) => {
  const [deletingIds, setDeletingIds] = useState(new Set());

  const handleDelete = async (docId) => {
    if (!window.confirm(`Are you sure you want to delete document ID: ${docId}?`)) {
      return;
    }

    // Add to deleting state
    setDeletingIds(prev => new Set(prev).add(docId));

    try {
      const response = await fetch(`/api/documents/${docId}`, {
        method: 'DELETE',
        credentials: 'include'
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || `Failed to delete with status ${response.status}`);
      }

      // Notify parent component
      if (onDelete) onDelete(docId);
    } catch (error) {
      console.error('Delete error:', error);
      alert(`Error deleting document: ${error.message}`);
    } finally {
      // Remove from deleting state
      setDeletingIds(prev => {
        const updated = new Set(prev);
        updated.delete(docId);
        return updated;
      });
    }
  };

  const renderDocuments = () => {
    if (isLoading) {
      return <div className="loading">Loading documents...</div>;
    }

    if (error) {
      return <p className="error">{error}</p>;
    }

    if (!documents || documents.length === 0) {
      return <p>No documents uploaded yet.</p>;
    }

    return documents.map(doc => (
      <div className="document-card" key={doc.id}>
        <div className="document-info">
          <div className="document-title">{doc.title}</div>
          Filename: {doc.filename} <br />
          ID: {doc.id}
        </div>
        <button 
          className="delete-btn" 
          onClick={() => handleDelete(doc.id)}
          disabled={deletingIds.has(doc.id)}
        >
          {deletingIds.has(doc.id) ? 'Deleting...' : 'Delete'}
        </button>
      </div>
    ));
  };

  return (
    <div className={`documents-section ${className || ''}`}>
      <h2>Document Library</h2>
      <button onClick={onRefresh} disabled={isLoading}>Refresh Documents</button>
      <div className="document-list">
        {renderDocuments()}
      </div>
    </div>
  );
};

export default DocumentsSection; 
import React, { useState } from 'react';
import './UploadSection.css';

const UploadSection = ({ onDocumentUploaded }) => {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [status, setStatus] = useState({ message: '', type: '' });
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleTitleChange = (e) => {
    setTitle(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      setStatus({ message: 'Please select a PDF file.', type: 'error' });
      return;
    }

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setStatus({ message: 'Only PDF files are supported.', type: 'error' });
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title.trim() || file.name);

    setStatus({ message: 'Uploading and processing document...', type: 'loading' });
    setIsUploading(true);

    try {
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || `Upload failed with status ${response.status}`);
      }

      setStatus({ 
        message: `Document '${result.title}' uploaded successfully (ID: ${result.doc_id})`, 
        type: 'success' 
      });
      
      // Clear form fields
      setFile(null);
      setTitle('');
      document.getElementById('fileUpload').value = '';
      
      // Notify parent component
      if (onDocumentUploaded) onDocumentUploaded();
    } catch (error) {
      console.error('Upload error:', error);
      setStatus({ message: `Error: ${error.message}`, type: 'error' });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="section upload-section">
      <h2>Upload PDF Document</h2>
      <p>Upload PDF documents to build the knowledge base.</p>
      <form onSubmit={handleSubmit}>
        <input 
          type="file" 
          id="fileUpload" 
          accept=".pdf" 
          required 
          onChange={handleFileChange}
          disabled={isUploading}
        />
        <input 
          type="text" 
          value={title} 
          onChange={handleTitleChange} 
          placeholder="Document Title (optional)"
          disabled={isUploading}
        />
        <button 
          type="submit" 
          disabled={isUploading}
        >
          {isUploading ? 'Uploading...' : 'Upload and Process'}
        </button>
      </form>
      {status.message && (
        <div className={`status ${status.type}`}>
          {status.message}
        </div>
      )}
    </div>
  );
};

export default UploadSection; 
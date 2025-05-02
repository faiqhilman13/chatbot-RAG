import { useState, useEffect } from 'react';
import { uploadDocument, fetchDocuments } from '../services/api';

export default function DocumentUpload() {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const response = await fetchDocuments();
      setDocuments(response.documents || []);
      setError(null);
    } catch (err) {
      setError('Failed to load documents: ' + err.message);
      console.error('Error loading documents:', err);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.includes('pdf')) {
      setError('Only PDF files are supported');
      event.target.value = '';
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const result = await uploadDocument(file);
      console.log('Upload result:', result);
      await loadDocuments(); // Refresh the list
      event.target.value = ''; // Reset file input
    } catch (err) {
      setError(err.message);
      console.error('Error uploading document:', err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Upload Document
        </label>
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileUpload}
          disabled={uploading}
          className="block w-full text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded-full file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-50 file:text-blue-700
            hover:file:bg-blue-100
            disabled:opacity-50 disabled:cursor-not-allowed"
        />
        {uploading && (
          <div className="mt-2">
            <div className="animate-pulse flex space-x-4">
              <div className="flex-1 space-y-4 py-1">
                <div className="h-3 bg-blue-200 rounded w-3/4"></div>
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">Uploading and processing document...</p>
          </div>
        )}
        {error && (
          <p className="mt-2 text-sm text-red-600 bg-red-50 p-2 rounded">{error}</p>
        )}
      </div>

      <div>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            Uploaded Documents
          </h3>
          <button
            onClick={loadDocuments}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Refresh
          </button>
        </div>
        {documents.length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {documents.map((doc) => (
              <li key={doc.id} className="py-3">
                <p className="text-sm font-medium text-gray-900">{doc.title}</p>
                <p className="text-xs text-gray-500">ID: {doc.id}</p>
                <p className="text-xs text-gray-500">Size: {doc.size}</p>
                {doc.chunk_count && (
                  <p className="text-xs text-gray-500">Chunks: {doc.chunk_count}</p>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-gray-500 bg-gray-50 p-4 rounded">
            No documents uploaded yet. Upload a PDF file to get started.
          </p>
        )}
      </div>
    </div>
  );
} 
/**
 * API service for communicating with the backend
 */

const API_BASE = '/api';

/**
 * Fetch list of uploaded documents
 * @returns {Promise<Array>} List of documents
 */
export async function fetchDocuments() {
  try {
    const response = await fetch(`${API_BASE}/documents`);
    if (!response.ok) {
      throw new Error(`Failed to fetch documents: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching documents:', error);
    throw error;
  }
}

/**
 * Upload a document to the backend
 * @param {File} file - The file to upload
 * @returns {Promise<Object>} Upload response
 */
export async function uploadDocument(file) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', file.name); // Using filename as title

    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Failed to upload document: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading document:', error);
    throw error;
  }
}

/**
 * Ask a question to the AI
 * @param {string} question - The question to ask
 * @returns {Promise<Object>} AI response with sources
 */
export async function askQuestion(question) {
  try {
    const response = await fetch(`${API_BASE}/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Failed to get answer: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error asking question:', error);
    throw error;
  }
} 
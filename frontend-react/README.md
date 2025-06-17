# Hybrid RAG Chatbot - React Frontend

This is a React.js implementation of the Hybrid RAG Chatbot frontend. It provides a modern, responsive UI for interacting with the RAG chatbot backend.

## Features

- Upload PDF documents to build the knowledge base
- View and manage uploaded documents
- Chat with the AI about the uploaded documents
- Responsive design that works on desktop and mobile devices

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- The RAG Chatbot backend running (default: http://localhost:8080)

### Installation

1. Navigate to the frontend-react directory:
   ```
   cd chatbot-RAG/frontend-react
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

4. The React app will open in your browser at http://localhost:5170

## Configuration

The React app is configured to proxy API requests to http://localhost:8080 by default. If your backend is running on a different port, update the "proxy" field in `package.json`.

## Building for Production

To build the app for production:

```
npm run build
```

This will create an optimized build in the `build` folder that can be deployed to a web server.

## Technology Stack

- React.js
- CSS3 with custom properties (variables)
- Fetch API for backend communication 
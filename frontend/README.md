# Frontend for Internal AI Chatbot

This folder contains the frontend code for the Internal AI Chatbot application.

## Getting Started

To run the frontend, you have two options:

### Option 1: Direct Frontend (May have CORS issues)

1. Start the Python HTTP server:
   ```
   python -m http.server 5001
   ```

2. Access the frontend at http://localhost:5001

### Option 2: Using the CORS Proxy (Recommended)

If you experience CORS issues when connecting to the backend API directly, you can use the included proxy server:

1. Install required dependencies:
   ```
   pip install requests
   ```

2. Start the proxy server:
   ```
   python proxy.py
   ```

3. Start the frontend HTTP server:
   ```
   python -m http.server 5001
   ```

4. Access the test page at http://localhost:5001/test.html

## Files

- `index.html` - Main chatbot interface
- `test.html` - Simple test page for API endpoints
- `proxy.py` - CORS proxy server to bypass browser security restrictions
- `static/` - Directory containing CSS and JavaScript files

## Troubleshooting

If you encounter issues:

1. Make sure the backend API is running (should be at http://localhost:8000)
2. Check your browser's developer console for error messages
3. Try using the proxy server as described in Option 2 
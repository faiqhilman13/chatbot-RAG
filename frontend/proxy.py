"""
Simple CORS proxy server for testing the chatbot API.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ProxyServer")

# API Configuration
API_URL = 'http://localhost:8000'
HOST = 'localhost'
PORT = 5002

class ProxyHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers()
    
    def do_GET(self):
        if self.path == '/health':
            try:
                response = requests.get(f"{API_URL}/health")
                self._set_headers(response.status_code)
                self.wfile.write(response.content)
                logger.info(f"Proxied GET /health - Status: {response.status_code}")
            except Exception as e:
                logger.error(f"Error proxying GET request: {str(e)}")
                self._set_headers(500)
                error_response = {"error": f"Proxy error: {str(e)}"}
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        if self.path == '/ask':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                # Forward the request to the actual API
                response = requests.post(
                    f"{API_URL}/api/v1/ask",
                    data=post_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                # Return the response from the API
                self._set_headers(response.status_code)
                self.wfile.write(response.content)
                logger.info(f"Proxied POST /ask - Status: {response.status_code}")
            except Exception as e:
                logger.error(f"Error proxying POST request: {str(e)}")
                self._set_headers(500)
                error_response = {"error": f"Proxy error: {str(e)}"}
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

def run_server():
    """Start the proxy server"""
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, ProxyHandler)
    logger.info(f"Starting CORS proxy server on http://{HOST}:{PORT}")
    logger.info(f"Proxying requests to {API_URL}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server() 
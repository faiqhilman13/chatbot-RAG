"""
Integration tests for authentication with the main application.
Tests that protected endpoints require authentication and work correctly after login.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
import json
import tempfile
import os
from unittest.mock import patch, Mock

@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)

class TestMainAppAuthentication:
    """Test authentication integration with main app endpoints."""
    
    def test_health_endpoint_public(self, client):
        """Test that health endpoint is accessible without authentication."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_root_endpoint_public(self, client):
        """Test that root endpoint is accessible without authentication."""
        # This might return 404 if frontend files don't exist, which is fine
        response = client.get("/")
        # Allow both 200 (if frontend exists) and 404 (if frontend doesn't exist)
        assert response.status_code in [200, 404]
    
    def test_protected_endpoints_require_auth(self, client):
        """Test that protected endpoints require authentication."""
        protected_endpoints = [
            ("POST", "/upload", {"files": {"file": ("test.pdf", b"fake pdf content", "application/pdf")}, "data": {"title": "Test"}}),
            ("GET", "/documents", None),
            ("DELETE", "/documents/test-id", None),
            ("POST", "/ask", {"question": "test question"}),
        ]
        
        for method, endpoint, payload in protected_endpoints:
            if method == "POST" and endpoint == "/upload":
                # Special handling for file upload
                response = client.post(endpoint, **payload)
            elif method == "POST":
                response = client.post(endpoint, json=payload)
            elif method == "GET":
                response = client.get(endpoint)
            elif method == "DELETE":
                response = client.delete(endpoint)
            
            assert response.status_code == 401, f"Endpoint {method} {endpoint} should require auth"
            data = response.json()
            assert "Authentication required" in data["detail"]


class TestAuthenticatedAccess:
    """Test that endpoints work correctly after authentication."""
    
    def test_login_and_access_protected_endpoints(self, client):
        """Test that endpoints work after successful login."""
        # First login
        login_response = client.post("/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert login_response.status_code == 200
        
        # Test that documents endpoint now works
        documents_response = client.get("/documents")
        assert documents_response.status_code == 200
        data = documents_response.json()
        assert "documents" in data
        
        # Test that ask endpoint works (even though it might return an error about no documents)
        ask_response = client.post("/ask", json={"question": "test question"})
        # Should return 200 but with a message about no documents
        assert ask_response.status_code == 200
        data = ask_response.json()
        assert "question" in data
        assert data["question"] == "test question"
    
    def test_logout_removes_access(self, client):
        """Test that logout removes access to protected endpoints."""
        # First login
        login_response = client.post("/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert login_response.status_code == 200
        
        # Verify access works
        documents_response = client.get("/documents")
        assert documents_response.status_code == 200
        
        # Logout
        logout_response = client.post("/auth/logout")
        assert logout_response.status_code == 200
        
        # Verify access is removed
        documents_response = client.get("/documents")
        assert documents_response.status_code == 401
    
    @patch('app.main.rag_retriever')
    def test_upload_with_auth_mock(self, mock_retriever, client):
        """Test document upload with authentication (mocked)."""
        # Mock the retriever to avoid actual file processing
        mock_retriever.load_vectorstore.return_value = True
        mock_retriever.vectorstore = Mock()
        mock_retriever.save_vectorstore.return_value = True
        
        # Mock prepare_documents to return fake chunks
        with patch('app.main.prepare_documents') as mock_prepare:
            mock_prepare.return_value = [Mock(page_content="test content")]
            
            # Login first
            login_response = client.post("/auth/login", json={
                "username": "admin",
                "password": "admin123"
            })
            assert login_response.status_code == 200
            
            # Try upload (this will fail due to mocking, but we can test the auth part)
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                tmp_file.write(b"fake pdf content")
                tmp_file.flush()
                tmp_file_name = tmp_file.name
            
            # File is now closed, safe to use
            try:
                with open(tmp_file_name, "rb") as f:
                    upload_response = client.post(
                        "/upload",
                        files={"file": ("test.pdf", f, "application/pdf")},
                        data={"title": "Test Document"}
                    )
                
                # Even if it fails for other reasons, it shouldn't be a 401
                assert upload_response.status_code != 401
                
            finally:
                try:
                    os.unlink(tmp_file_name)
                except (PermissionError, FileNotFoundError):
                    # On Windows, sometimes the file is still in use
                    pass


class TestAuthenticationFlow:
    """Test complete authentication flow."""
    
    def test_full_authentication_flow(self, client):
        """Test a complete authentication flow."""
        # 1. Check initial status (not authenticated)
        status_response = client.get("/auth/status")
        assert status_response.status_code == 200
        assert status_response.json()["authenticated"] is False
        
        # 2. Try accessing protected endpoint (should fail)
        protected_response = client.get("/documents")
        assert protected_response.status_code == 401
        
        # 3. Login
        login_response = client.post("/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert login_response.status_code == 200
        
        # 4. Check status after login (should be authenticated)
        status_response = client.get("/auth/status")
        assert status_response.status_code == 200
        data = status_response.json()
        assert data["authenticated"] is True
        assert data["user"] == "admin"
        
        # 5. Access protected endpoint (should work)
        protected_response = client.get("/documents")
        assert protected_response.status_code == 200
        
        # 6. Get user info
        user_info_response = client.get("/auth/me")
        assert user_info_response.status_code == 200
        data = user_info_response.json()
        assert data["user"] == "admin"
        
        # 7. Logout
        logout_response = client.post("/auth/logout")
        assert logout_response.status_code == 200
        
        # 8. Check status after logout (should not be authenticated)
        status_response = client.get("/auth/status")
        assert status_response.status_code == 200
        assert status_response.json()["authenticated"] is False
        
        # 9. Try accessing protected endpoint again (should fail)
        protected_response = client.get("/documents")
        assert protected_response.status_code == 401


class TestSecurityFeatures:
    """Test security features and edge cases."""
    
    def test_invalid_login_attempts(self, client):
        """Test multiple invalid login attempts."""
        # Test completely missing fields (should be validation error)
        missing_field_tests = [
            {"username": "admin"},  # Missing password
            {"password": "admin123"},  # Missing username
        ]
        
        for creds in missing_field_tests:
            response = client.post("/auth/login", json=creds)
            assert response.status_code == 422  # Validation error
        
        # Test invalid credentials (should be authentication error)
        invalid_credentials = [
            {"username": "admin", "password": "wrong"},
            {"username": "hacker", "password": "admin123"},
            {"username": "admin", "password": ""},
            {"username": "", "password": "admin123"},
        ]
        
        for creds in invalid_credentials:
            response = client.post("/auth/login", json=creds)
            # All of these should be authentication errors (401)
            # because they reach the authentication logic
            assert response.status_code == 401
    
    def test_session_isolation(self, client):
        """Test that different client instances have isolated sessions."""
        client1 = TestClient(app)
        client2 = TestClient(app)
        
        # Login with client1
        login_response = client1.post("/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert login_response.status_code == 200
        
        # Client1 should have access
        response1 = client1.get("/documents")
        assert response1.status_code == 200
        
        # Client2 should not have access
        response2 = client2.get("/documents")
        assert response2.status_code == 401 
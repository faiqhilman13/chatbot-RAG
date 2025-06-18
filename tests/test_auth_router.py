"""
Unit tests for the authentication router.
Tests login, logout, and status endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.routers.auth import router
import json

# Create a test app with the auth router
def create_test_app():
    app = FastAPI()
    # Add session middleware (required for auth)
    app.add_middleware(SessionMiddleware, secret_key="test-secret-key")
    app.include_router(router)
    return app

@pytest.fixture
def client():
    """Create a test client with session middleware."""
    app = create_test_app()
    return TestClient(app)

class TestLogin:
    """Test login endpoint."""
    
    def test_login_success(self, client):
        """Test successful login with valid credentials."""
        response = client.post("/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Login successful"
        assert data["user"] == "admin"
    
    def test_login_invalid_username(self, client):
        """Test login with invalid username."""
        response = client.post("/auth/login", json={
            "username": "nonexistent",
            "password": "admin123"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid username or password" in data["detail"]
    
    def test_login_invalid_password(self, client):
        """Test login with invalid password."""
        response = client.post("/auth/login", json={
            "username": "admin",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid username or password" in data["detail"]
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields."""
        # Missing password
        response = client.post("/auth/login", json={
            "username": "admin"
        })
        assert response.status_code == 422  # Validation error
        
        # Missing username
        response = client.post("/auth/login", json={
            "password": "admin123"
        })
        assert response.status_code == 422  # Validation error


class TestLogout:
    """Test logout endpoint."""
    
    def test_logout_success(self, client):
        """Test successful logout when authenticated."""
        # First login
        login_response = client.post("/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert login_response.status_code == 200
        
        # Then logout
        logout_response = client.post("/auth/logout")
        assert logout_response.status_code == 200
        
        data = logout_response.json()
        assert data["status"] == "success"
        assert data["message"] == "Logout successful"
    
    def test_logout_unauthenticated(self, client):
        """Test logout when not authenticated."""
        response = client.post("/auth/logout")
        assert response.status_code == 401
        data = response.json()
        assert "Authentication required" in data["detail"]


class TestAuthStatus:
    """Test authentication status endpoint."""
    
    def test_status_authenticated(self, client):
        """Test status when user is authenticated."""
        # First login
        login_response = client.post("/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert login_response.status_code == 200
        
        # Check status
        status_response = client.get("/auth/status")
        assert status_response.status_code == 200
        
        data = status_response.json()
        assert data["authenticated"] is True
        assert data["user"] == "admin"
    
    def test_status_not_authenticated(self, client):
        """Test status when user is not authenticated."""
        response = client.get("/auth/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["authenticated"] is False
        assert data.get("user") is None


class TestUserInfo:
    """Test user info endpoint."""
    
    def test_user_info_authenticated(self, client):
        """Test getting user info when authenticated."""
        # First login
        login_response = client.post("/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert login_response.status_code == 200
        
        # Get user info
        info_response = client.get("/auth/me")
        assert info_response.status_code == 200
        
        data = info_response.json()
        assert data["user"] == "admin"
        assert data["authenticated"] is True
    
    def test_user_info_not_authenticated(self, client):
        """Test getting user info when not authenticated."""
        response = client.get("/auth/me")
        assert response.status_code == 401
        data = response.json()
        assert "Authentication required" in data["detail"]


class TestSessionPersistence:
    """Test session persistence across requests."""
    
    def test_session_persists_after_login(self, client):
        """Test that session persists after login."""
        # Login
        login_response = client.post("/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert login_response.status_code == 200
        
        # Make multiple authenticated requests
        for _ in range(3):
            status_response = client.get("/auth/status")
            assert status_response.status_code == 200
            data = status_response.json()
            assert data["authenticated"] is True
            assert data["user"] == "admin"
    
    def test_session_cleared_after_logout(self, client):
        """Test that session is cleared after logout."""
        # Login
        login_response = client.post("/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert login_response.status_code == 200
        
        # Verify authenticated
        status_response = client.get("/auth/status")
        assert status_response.json()["authenticated"] is True
        
        # Logout
        logout_response = client.post("/auth/logout")
        assert logout_response.status_code == 200
        
        # Verify not authenticated
        status_response = client.get("/auth/status")
        assert status_response.json()["authenticated"] is False
        
        # Verify protected endpoints require auth again
        info_response = client.get("/auth/me")
        assert info_response.status_code == 401


class TestEndpointSecurity:
    """Test endpoint security behavior."""
    
    def test_protected_endpoints_require_auth(self, client):
        """Test that protected endpoints require authentication."""
        protected_endpoints = [
            ("POST", "/auth/logout"),
            ("GET", "/auth/me"),
        ]
        
        for method, endpoint in protected_endpoints:
            if method == "POST":
                response = client.post(endpoint)
            else:
                response = client.get(endpoint)
            
            assert response.status_code == 401, f"Endpoint {method} {endpoint} should require auth"
            data = response.json()
            assert "Authentication required" in data["detail"]
    
    def test_public_endpoints_work_without_auth(self, client):
        """Test that public endpoints work without authentication."""
        public_endpoints = [
            ("GET", "/auth/status"),
        ]
        
        for method, endpoint in public_endpoints:
            if method == "POST":
                response = client.post(endpoint, json={})
            else:
                response = client.get(endpoint)
            
            assert response.status_code == 200, f"Endpoint {method} {endpoint} should work without auth" 
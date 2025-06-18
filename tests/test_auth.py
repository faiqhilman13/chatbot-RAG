"""
Unit tests for the authentication module.
Tests password hashing, user authentication, and session management.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from app.auth import (
    verify_password, 
    authenticate_user, 
    create_session, 
    destroy_session,
    get_current_user,
    is_authenticated,
    require_auth,
    init_admin_password,
    USERS,
    pwd_context
)


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_password_hashing_works(self):
        """Test that password hashing creates valid hashes."""
        password = "test123"
        hashed = pwd_context.hash(password)
        
        # Hash should be different from original password
        assert hashed != password
        assert len(hashed) > 20  # bcrypt hashes are long
        assert hashed.startswith("$2b$")  # bcrypt format
    
    def test_verify_password_success(self):
        """Test successful password verification."""
        password = "admin123"
        hashed = pwd_context.hash(password)
        
        result = verify_password(password, hashed)
        assert result is True
    
    def test_verify_password_failure(self):
        """Test failed password verification."""
        password = "admin123"
        wrong_password = "wrong123"
        hashed = pwd_context.hash(password)
        
        result = verify_password(wrong_password, hashed)
        assert result is False
    
    def test_admin_password_initialization(self):
        """Test that admin password is properly initialized."""
        # Admin user should exist
        assert "admin" in USERS
        assert USERS["admin"]["hashed_password"] is not None
        
        # Should be able to verify admin password
        admin_hash = USERS["admin"]["hashed_password"]
        assert verify_password("admin123", admin_hash) is True
        assert verify_password("wrong", admin_hash) is False


class TestUserAuthentication:
    """Test user authentication logic."""
    
    def test_authenticate_valid_user(self):
        """Test authentication with valid credentials."""
        user = authenticate_user("admin", "admin123")
        
        assert user is not None
        assert user["username"] == "admin"
        assert user["is_active"] is True
    
    def test_authenticate_invalid_username(self):
        """Test authentication with invalid username."""
        user = authenticate_user("nonexistent", "admin123")
        assert user is None
    
    def test_authenticate_invalid_password(self):
        """Test authentication with invalid password."""
        user = authenticate_user("admin", "wrongpassword")
        assert user is None
    
    def test_authenticate_inactive_user(self):
        """Test authentication with inactive user."""
        # Temporarily make admin inactive
        original_status = USERS["admin"]["is_active"]
        USERS["admin"]["is_active"] = False
        
        try:
            user = authenticate_user("admin", "admin123")
            assert user is None
        finally:
            # Restore original status
            USERS["admin"]["is_active"] = original_status


class TestSessionManagement:
    """Test session management functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_request = Mock()
        self.mock_request.session = {}
    
    def test_create_session(self):
        """Test session creation."""
        create_session(self.mock_request, "admin")
        
        assert self.mock_request.session["user"] == "admin"
        assert self.mock_request.session["authenticated"] is True
    
    def test_destroy_session(self):
        """Test session destruction."""
        # First create a session
        self.mock_request.session = {"user": "admin", "authenticated": True}
        
        # Then destroy it
        destroy_session(self.mock_request)
        
        # Session should be cleared
        assert len(self.mock_request.session) == 0
    
    def test_get_current_user_authenticated(self):
        """Test getting current user when authenticated."""
        self.mock_request.session = {"user": "admin", "authenticated": True}
        
        user = get_current_user(self.mock_request)
        assert user == "admin"
    
    def test_get_current_user_not_authenticated(self):
        """Test getting current user when not authenticated."""
        # Empty session
        user = get_current_user(self.mock_request)
        assert user is None
        
        # Partial session
        self.mock_request.session = {"user": "admin"}  # Missing authenticated flag
        user = get_current_user(self.mock_request)
        assert user is None
    
    def test_is_authenticated_true(self):
        """Test authentication check when user is authenticated."""
        self.mock_request.session = {"user": "admin", "authenticated": True}
        
        result = is_authenticated(self.mock_request)
        assert result is True
    
    def test_is_authenticated_false(self):
        """Test authentication check when user is not authenticated."""
        # Empty session
        result = is_authenticated(self.mock_request)
        assert result is False
        
        # Partial session
        self.mock_request.session = {"user": "admin"}  # Missing authenticated flag
        result = is_authenticated(self.mock_request)
        assert result is False


class TestAuthenticationDependency:
    """Test FastAPI authentication dependencies."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_request = Mock()
        self.mock_request.session = {}
    
    def test_require_auth_success(self):
        """Test require_auth dependency with authenticated user."""
        self.mock_request.session = {"user": "admin", "authenticated": True}
        
        user = require_auth(self.mock_request)
        assert user == "admin"
    
    def test_require_auth_failure(self):
        """Test require_auth dependency with unauthenticated user."""
        # Empty session should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            require_auth(self.mock_request)
        
        assert exc_info.value.status_code == 401
        assert "Authentication required" in str(exc_info.value.detail)


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_verify_password_with_invalid_hash(self):
        """Test password verification with malformed hash."""
        result = verify_password("admin123", "invalid_hash")
        assert result is False
    
    def test_session_with_missing_keys(self):
        """Test session handling with missing keys."""
        mock_request = Mock()
        
        # Session with only user but no authenticated flag
        mock_request.session = {"user": "admin"}
        assert is_authenticated(mock_request) is False
        assert get_current_user(mock_request) is None
        
        # Session with only authenticated flag but no user
        mock_request.session = {"authenticated": True}
        assert is_authenticated(mock_request) is False
        assert get_current_user(mock_request) is None 
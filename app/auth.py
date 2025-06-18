"""
Authentication module for the RAG chatbot.
Contains all authentication logic including password hashing,
session management, and auth dependencies.
"""

from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from typing import Optional
import logging
from app.config import ADMIN_PASSWORD

logger = logging.getLogger(__name__)

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Simple user storage (in production, use a database)
USERS = {
    "admin": {
        "username": "admin",
        "hashed_password": None,  # Will be set below
        "is_active": True
    }
}

# Initialize admin password hash
def init_admin_password():
    """Initialize the admin password hash."""
    hashed = pwd_context.hash(ADMIN_PASSWORD)
    USERS["admin"]["hashed_password"] = hashed
    logger.info("Admin password hash initialized")
    return hashed

# Initialize on module load
admin_hash = init_admin_password()
# Removed sensitive hash logging for security

# Password verification functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        # Removed sensitive logging for security
        return result
    except Exception as e:
        logger.error("Password verification error occurred")  # Don't log actual error details
        return False

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate a user with username and password."""
    logger.info(f"Attempting to authenticate user: {username}")
    
    if username not in USERS:
        logger.warning(f"User not found: {username}")
        return None
    
    user = USERS[username]
    logger.info(f"User found: {user['username']}, active: {user['is_active']}")
    
    if not user["is_active"]:
        logger.warning(f"User inactive: {username}")
        return None
    
    if not verify_password(password, user["hashed_password"]):
        logger.warning(f"Password verification failed for user: {username}")
        return None
    
    logger.info(f"Authentication successful for user: {username}")
    return user

# Session management
def create_session(request: Request, username: str):
    """Create a session for the authenticated user."""
    request.session["user"] = username
    request.session["authenticated"] = True
    logger.info(f"Session created for user: {username}")

def destroy_session(request: Request):
    """Destroy the user session."""
    if "user" in request.session:
        user = request.session["user"]
        logger.info(f"Destroying session for user: {user}")
    request.session.clear()

def get_current_user(request: Request) -> Optional[str]:
    """Get the current authenticated user from session."""
    if request.session.get("authenticated") and request.session.get("user"):
        return request.session["user"]
    return None

def is_authenticated(request: Request) -> bool:
    """Check if the current request is authenticated."""
    return request.session.get("authenticated", False) and request.session.get("user") is not None

# Authentication dependency
def require_auth(request: Request) -> str:
    """FastAPI dependency that requires authentication."""
    if not is_authenticated(request):
        logger.warning("Authentication required but user not authenticated")
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    user = get_current_user(request)
    logger.info(f"Authentication check passed for user: {user}")
    return user

# Optional authentication dependency (for endpoints that work with or without auth)
def optional_auth(request: Request) -> Optional[str]:
    """FastAPI dependency for optional authentication."""
    return get_current_user(request) 
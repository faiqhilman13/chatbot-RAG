"""
Authentication router for login, logout, and status endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.auth import authenticate_user, create_session, destroy_session, get_current_user, require_auth
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Request models
class LoginRequest(BaseModel):
    username: str
    password: str

# Response models
class LoginResponse(BaseModel):
    status: str
    message: str
    user: str

class StatusResponse(BaseModel):
    authenticated: bool
    user: str = None

@router.post("/login", response_model=LoginResponse)
async def login(request: Request, credentials: LoginRequest):
    """
    Authenticate user and create session.
    """
    logger.info(f"Login attempt for username: {credentials.username}")
    
    # Authenticate user
    user = authenticate_user(credentials.username, credentials.password)
    
    if not user:
        logger.warning(f"Login failed for username: {credentials.username}")
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    # Create session
    create_session(request, user["username"])
    
    logger.info(f"Login successful for username: {credentials.username}")
    return LoginResponse(
        status="success",
        message="Login successful",
        user=user["username"]
    )

@router.post("/logout")
async def logout(request: Request, current_user: str = Depends(require_auth)):
    """
    Logout user and destroy session.
    """
    logger.info(f"Logout request from user: {current_user}")
    
    # Destroy session
    destroy_session(request)
    
    logger.info(f"Logout successful for user: {current_user}")
    return JSONResponse(
        content={"status": "success", "message": "Logout successful"},
        status_code=200
    )

@router.get("/status", response_model=StatusResponse)
async def get_auth_status(request: Request):
    """
    Get current authentication status.
    """
    current_user = get_current_user(request)
    
    if current_user:
        logger.info(f"Auth status check - authenticated user: {current_user}")
        return StatusResponse(authenticated=True, user=current_user)
    else:
        logger.info("Auth status check - not authenticated")
        return StatusResponse(authenticated=False)

@router.get("/me")
async def get_current_user_info(current_user: str = Depends(require_auth)):
    """
    Get current user information (requires authentication).
    """
    logger.info(f"User info request from: {current_user}")
    return JSONResponse(
        content={"user": current_user, "authenticated": True},
        status_code=200
    ) 
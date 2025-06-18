#!/usr/bin/env python3
"""
Security setup script for RAG Chatbot
Generates secure environment variables
"""

import secrets
import os

def generate_security_env():
    """Generate secure environment variables"""
    
    # Generate secure session secret
    session_secret = secrets.token_urlsafe(32)
    
    print("🔐 Security Environment Variables Generated:")
    print("=" * 50)
    print(f"SESSION_SECRET_KEY={session_secret}")
    print("ADMIN_PASSWORD=admin123")  # Default for demo
    print()
    print("📋 To set these in PowerShell, run:")
    print(f'$env:SESSION_SECRET_KEY="{session_secret}"')
    print('$env:ADMIN_PASSWORD="admin123"')
    print()
    print("🚀 Then start the backend with:")
    print("python -m uvicorn app.main:app --reload --port 8001")
    print()
    print("🌐 And start the frontend with:")
    print("cd frontend-react")
    print("npm start")
    print()
    print("⚠️  IMPORTANT: Change ADMIN_PASSWORD in production!")

if __name__ == "__main__":
    generate_security_env() 
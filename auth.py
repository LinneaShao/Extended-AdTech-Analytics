"""
Authentication utilities for JWT token management.
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional
import os

# Configuration
JWT_SECRET = "adtech_secret_2024"
JWT_ALGORITHM = "HS256"
DEFAULT_EXPIRE_MINUTES = 60

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=DEFAULT_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def authenticate_user(username: str, password: str) -> bool:
    """Simple user authentication"""
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    return username == "admin" and password == admin_password

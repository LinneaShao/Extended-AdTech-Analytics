"""
AdTech Analytics Platform
Campaign performance tracking and analysis service.
"""

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import jwt
from datetime import datetime, timedelta
import pandas as pd
import io
import os
from pydantic import BaseModel

from data_processing import process_csv_data
from database import save_data, get_stats
from cache import CacheManager

# Configuration
JWT_SECRET = "adtech_secret_2024"
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

app = FastAPI(
    title="AdTech Analytics",
    description="Campaign performance tracking and analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()
cache = CacheManager()

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

def create_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    user_password = os.getenv('USER_PASSWORD', 'user123')
    
    # Support multiple users
    valid_users = {
        "admin": admin_password,
        "user": user_password,
        "analyst": "analyst123",
        "manager": "manager123"
    }
    
    if request.username in valid_users and request.password == valid_users[request.username]:
        access_token = create_token(data={"sub": request.username})
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/data/upload")
async def upload_data(
    file: UploadFile = File(...),
    current_user: str = Depends(verify_token)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    
    try:
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        processed_data = process_csv_data(df)
        records_saved = save_data(processed_data)
        cache.clear()
        
        return {
            "message": "Data uploaded successfully",
            "records_processed": len(processed_data),
            "records_saved": records_saved
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Processing error: {str(e)}")

@app.get("/data/stats")
async def get_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    channel: Optional[str] = None,
    current_user: str = Depends(verify_token)
):
    cache_key = f"stats_{start_date}_{end_date}_{channel}"
    
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    try:
        stats = get_stats(start_date=start_date, end_date=end_date, channel=channel)
        cache.set(cache_key, stats, ttl=300)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "AdTech Analytics API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "login": "/auth/login",
            "upload": "/data/upload",
            "stats": "/data/stats"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

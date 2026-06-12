from fastapi import HTTPException, Depends, status, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict
from typing import Optional
import time
import os
import re

from app.database import get_db
from app.models.schemas import User, Organization




security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "finexri-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 24))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
request_counts = defaultdict(list)

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Pydantic schemas ──────────────────────────────────────────────────────────


from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    org_name: str
    
class LoginRequest(BaseModel):
    email: str
    password: str


# ── Helpers ───────────────────────────────────────────────────────────────────

def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug


def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password must be 72 characters or fewer"
        )

    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(optional_security),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def rate_limit(max_requests: int = 100, window_seconds: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            client_ip = "default"
            now = time.time()
            request_counts[client_ip] = [
                t for t in request_counts[client_ip] if now - t < window_seconds
            ]
            if len(request_counts[client_ip]) >= max_requests:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            request_counts[client_ip].append(now)
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# ── Auth routes ───────────────────────────────────────────────────────────────

@auth_router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email.lower()).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create org with unique slug
    base_slug = _slugify(req.org_name)
    slug = base_slug
    counter = 1
    while db.query(Organization).filter(Organization.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    org = Organization(name=req.org_name, slug=slug, plan="free")
    db.add(org)
    db.flush()

    user = User(
        email=req.email.lower(),
        full_name=req.full_name,
        password_hash=hash_password(req.password),
        role="owner",
        org_id=org.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        },
        "organization": {
            "id": org.id,
            "name": org.name,
            "slug": org.slug,
            "plan": org.plan,
        },
    }


@auth_router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    org = db.query(Organization).filter(Organization.id == user.org_id).first()
    token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        },
        "organization": {
            "id": org.id if org else None,
            "name": org.name if org else None,
            "slug": org.slug if org else None,
            "plan": org.plan if org else "free",
        },
    }


@auth_router.get("/me")
def get_me(current_user: User = Depends(verify_token), db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role,
        },
        "organization": {
            "id": org.id if org else None,
            "name": org.name if org else None,
            "slug": org.slug if org else None,
            "plan": org.plan if org else "free",
        },
    }

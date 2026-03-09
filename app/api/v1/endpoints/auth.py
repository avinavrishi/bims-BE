"""
Authentication Endpoints (JWT + sessions + refresh token rotation)
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.dependencies import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    hash_refresh_token,
    verify_password,
)
from app.models.auth_models import AuthSession, LoginAudit, LoginStatus, RefreshToken
from app.models.profile import Profile, Creator, CreatorVerificationStatus
from app.models.user import User, UserRole, UserStatus
from app.models.brand import Brand
from app.schemas.user import TokenPair, UserCreate, BrandUserCreate, UserLogin, UserResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new creator."""
    result = db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    password_hash = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=password_hash,
        role=UserRole.CREATOR,
        status=UserStatus.ACTIVE,
    )
    db.add(new_user)
    db.flush()

    # Placeholder display_name until creator sets username on first login
    display_name = user_data.email.split("@")[0] if user_data.email else "Creator"
    profile = Profile(
        user_id=new_user.id,
        display_name=display_name,
    )
    creator = Creator(
        user_id=new_user.id,
        total_earnings=0.0,
        wallet_balance=0.0,
        verification_status=CreatorVerificationStatus.PENDING,
    )
    db.add(profile)
    db.add(creator)

    db.commit()
    db.refresh(new_user)
    return new_user


@router.post(
    "/register-brand",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_brand(user_data: BrandUserCreate, db: Session = Depends(get_db)):
    """Register a new brand user and associated Brand profile."""
    result = db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    password_hash = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=password_hash,
        role=UserRole.BRAND,
        status=UserStatus.ACTIVE,
    )
    db.add(new_user)
    db.flush()

    brand = Brand(
        user_id=new_user.id,
        company_name=user_data.company_name,
        industry=user_data.industry,
        website=user_data.website,
    )
    db.add(brand)

    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenPair)
async def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Login by email/password and receive a JWT access token. Works for creators, brands, and admins."""
    result = db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.password_hash):
        audit = LoginAudit(
            user_id=user.id if user else None,
            status=LoginStatus.FAILED,
        )
        db.add(audit)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
        )

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    device_info = request.headers.get("x-device-info")

    session_expires_at = datetime.utcnow() + timedelta(days=settings.SESSION_EXPIRE_DAYS)
    session = AuthSession(
        user_id=user.id,
        device_info=device_info,
        ip_address=ip_address,
        user_agent=user_agent,
        is_active=True,
        last_used_at=datetime.utcnow(),
        expires_at=session_expires_at,
    )
    db.add(session)
    db.flush()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "role": user.role.value,
            "session_id": session.id,
        },
        expires_delta=access_token_expires,
    )

    refresh_token_raw = create_refresh_token()
    refresh_expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh = RefreshToken(
        session_id=session.id,
        token_hash=hash_refresh_token(refresh_token_raw),
        revoked=False,
        expires_at=refresh_expires_at,
    )
    db.add(refresh)

    audit = LoginAudit(
        user_id=user.id,
        status=LoginStatus.SUCCESS,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(audit)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token_raw,
        "session_id": session.id,
    }


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(data: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    """Refresh token rotation: validate refresh token, revoke old, issue new pair."""
    token_hash = hash_refresh_token(data.refresh_token)
    result = db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    rt = result.scalar_one_or_none()
    if not rt or rt.revoked or (rt.expires_at and rt.expires_at < datetime.utcnow()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    result = db.execute(select(AuthSession).where(AuthSession.id == rt.session_id))
    session = result.scalar_one_or_none()
    if not session or not session.is_active or (session.expires_at and session.expires_at < datetime.utcnow()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    result = db.execute(select(User).where(User.id == session.user_id))
    user = result.scalar_one_or_none()
    if not user or user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not active")

    rt.revoked = True
    session.last_used_at = datetime.utcnow()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "role": user.role.value,
            "session_id": session.id,
        },
        expires_delta=access_token_expires,
    )

    new_refresh_raw = create_refresh_token()
    refresh_expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    new_rt = RefreshToken(
        session_id=session.id,
        token_hash=hash_refresh_token(new_refresh_raw),
        revoked=False,
        expires_at=refresh_expires_at,
    )
    db.add(new_rt)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_raw,
        "session_id": session.id,
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logout the current session (multi-device safe). Requires Authorization: Bearer <access_token>."""
    from app.core.security import decode_access_token

    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header")

    payload = decode_access_token(parts[1])
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token missing session_id")

    result = db.execute(
        select(AuthSession).where(
            AuthSession.id == session_id,
            AuthSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if session:
        session.is_active = False
        db.execute(
            update(RefreshToken).where(RefreshToken.session_id == session.id).values(revoked=True)
        )
        db.commit()
    return None


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

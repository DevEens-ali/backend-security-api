
from datetime import datetime, timezone
from app.schemas import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    UserResponse,
    TokenResponse,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    Cookie,
    status,
)
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User, RefreshToken
from app.schemas import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse,
)
from app.services.auth_service import hash_password, verify_password
from app.services.token_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.services.rate_limit_service import check_login_rate_limit


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        role="user",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    # Rate limit check
    ip_address = (
        request.client.host
        if request.client
        else "unknown"
    )

    check_login_rate_limit(ip_address)

    # Find user
    user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    # Verify credentials
    if not user or not verify_password(
        data.password,
        user.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # Get refresh token expiry
    payload = decode_token(refresh_token)
    expires_at = datetime.fromtimestamp(
        payload["exp"],
        tz=timezone.utc,
    ).replace(tzinfo=None)

    # Save refresh token
    stored_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=expires_at,
        revoked=False,
    )

    db.add(stored_token)
    db.commit()

    # Set HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Local HTTP development only
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/auth",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if refresh_token:
        stored_token = (
            db.query(RefreshToken)
            .filter(RefreshToken.token == refresh_token)
            .first()
        )

        if stored_token and not stored_token.revoked:
            stored_token.revoked = True
            db.commit()

    response.delete_cookie(
        key="refresh_token",
        path="/auth",
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return {
        "message": "Logged out successfully"
    }

@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    # Check whether refresh token exists in cookie
    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token is required",
        )

    # Find token in database
    stored_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == refresh_token)
        .first()
    )

    # Reject missing or revoked tokens
    if not stored_token or stored_token.revoked:
        raise HTTPException(
            status_code=401,
            detail="Invalid or revoked refresh token",
        )

    # Validate token signature and expiry
    try:
        payload = decode_token(refresh_token)
    except Exception:
        stored_token.revoked = True
        db.commit()
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token",
        )

    # Ensure this is a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Refresh token required",
        )

    # Ensure database record matches token owner
    if payload.get("user_id") != stored_token.user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    # Rotate: revoke old token
    stored_token.revoked = True

    # Create new token pair
    new_access_token = create_access_token(stored_token.user_id)
    new_refresh_token = create_refresh_token(stored_token.user_id)

    # Store new refresh token
    new_payload = decode_token(new_refresh_token)
    expires_at = datetime.fromtimestamp(
        new_payload["exp"],
        tz=timezone.utc,
    ).replace(tzinfo=None)

    new_stored_token = RefreshToken(
        user_id=stored_token.user_id,
        token=new_refresh_token,
        expires_at=expires_at,
        revoked=False,
    )

    db.add(new_stored_token)
    db.commit()

    # Replace HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,  # Local HTTP development only
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/auth",
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }

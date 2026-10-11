
from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.models import User
from app.schemas import UserResponse
from app.dependencies.rbac import require_roles


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user
@router.get("/admin-only")
def admin_only(
    current_user: User = Depends(require_roles("admin"))
):
    return {
        "message": "Welcome, Admin!",
        "user": current_user.name,
        "role": current_user.role
    }


@router.get("/moderator-only")
def moderator_only(
    current_user: User = Depends(
        require_roles("moderator", "admin")
    )
):
    return {
        "message": "Welcome, Moderator!",
        "user": current_user.name,
        "role": current_user.role
    }


@router.get("/user-area")
def user_area(
    current_user: User = Depends(
        require_roles("user", "admin")
    )
):
    return {
        "message": "Welcome to the user area!",
        "user": current_user.name,
        "role": current_user.role
    }

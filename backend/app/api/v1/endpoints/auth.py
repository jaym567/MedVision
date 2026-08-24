# backend/app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserRead, CurrentUser
from app.core.exceptions import DuplicateResourceError, AuthenticationError, ValidationError, InactiveUserError
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.

    **WARNING**: This endpoint uses mock/de-identified data only.
    Do not submit real PHI or personal information.

    - **email**: Must be unique, will be normalized to lowercase
    - **password**: Minimum 8 characters
    - **role**: Must be one of: physician, researcher, admin
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.register_user(user_data)
        return user
    except DuplicateResourceError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and receive JWT access token.

    Returns:
        - **access_token**: JWT token for authentication
        - **token_type**: Always "bearer"
        - **expires_in**: Token expiration time in seconds
        - **user**: Basic user information
    """
    try:
        auth_service = AuthService(db)
        token_response = await auth_service.authenticate_user(login_data)
        return token_response
    except (AuthenticationError, InactiveUserError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=CurrentUser)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.

    Requires valid JWT token in Authorization header.
    """
    return CurrentUser.model_validate(current_user)

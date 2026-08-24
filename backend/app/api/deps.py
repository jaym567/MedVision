# backend/app/api/deps.py
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.core.security import decode_access_token
from app.core.exceptions import AuthenticationError, ResourceNotFoundError
from app.repositories.user_repository import UserRepository
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    Raises:
        HTTPException: 401 if token invalid or user not found/inactive
    """
    try:
        # Decode and validate token
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid token: missing subject")

        # Fetch user from database
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)

        if user is None:
            raise AuthenticationError(f"User {user_id} not found")

        if not user.is_active:
            raise AuthenticationError("User account is inactive")

        return user

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Type alias for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]

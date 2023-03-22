from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_async_session
from schemas.users import UserRead, UserCreate
from services.users import fastapi_users, auth_backend

api_router = APIRouter()

api_router.include_router(
    fastapi_users.get_auth_router(auth_backend, requires_verification=False),
    prefix='/auth/jwt',
    tags=['auth'],
)

api_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
)


@api_router.get('/ping', tags=['main'])
async def ping_db(
        *,
        db: AsyncSession = Depends(get_async_session),
) -> Any:
    """
    Check DB connection status
    """

    try:
        await db.connection()
        connection_status = True
    except Exception:
        connection_status = False

    return {'Connected': connection_status}

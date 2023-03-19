from fastapi import APIRouter

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

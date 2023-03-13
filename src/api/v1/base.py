from fastapi import APIRouter, Depends

from db.db import User
from schemas.users import UserRead, UserCreate
from services.users import fastapi_users, auth_backend, current_active_user

api_router = APIRouter()

api_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)

api_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)


@api_router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}

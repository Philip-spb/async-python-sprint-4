from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_async_session
from schemas import base as base_schema
from schemas.users import UserRead, UserCreate
from services.shortlink import short_link_crud
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


@api_router.get("/", response_model=List[base_schema.ShortLinkShenma])
async def read_entities(db: AsyncSession = Depends(get_async_session)) -> Any:
    entities = await short_link_crud.get_multi(db=db)
    return entities


@api_router.get("/{id}", response_model=base_schema.ShortLinkShenma)
async def read_entity(*, db: AsyncSession = Depends(get_async_session), id: int) -> Any:
    """
    Get by ID.
    """
    entity = await short_link_crud.get(db=db, id=id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return entity

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_async_session
from models.general import User
from schemas.base import ShortLinkShenma, ShortLinkCreate, ShortLinkToDBBase
from services.helpers import id_generator, is_valid_url
from services.shortlink import short_link_crud
from services.users import current_active_user

shorten_url_router = APIRouter()


@shorten_url_router.post('/', response_model=ShortLinkShenma, status_code=status.HTTP_201_CREATED)
async def create_create_short_link(
        *,
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
        link: ShortLinkCreate,
) -> Any:
    """
    Create new short link.
    """

    if not is_valid_url(link.original_url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This is not the URL')

    short_link = id_generator()

    new_link = ShortLinkToDBBase(
        short_url=short_link,
        original_url=link.original_url,
        owner_id=user.id if user else None
    )
    entity = await short_link_crud.create(db=db, obj_in=new_link)
    return entity


@shorten_url_router.get('/{short_url}')
async def redirect_to_link(
        *,
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
        short_url: str
) -> Any:
    entity = await short_link_crud.get_by_short_url(db=db, short_url=short_url)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    # TODO Добавить сохранения лога перехода
    # TODO Добавить проверку на приватность
    return RedirectResponse(url=entity.original_url)

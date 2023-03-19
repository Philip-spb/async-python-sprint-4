from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_async_session
from models.general import User
from schemas.access_log import AccessLogToDBBase, AccessLogStatistic
from schemas.short_link import (ShortLinkSchemaCreate, ShortLinkSchemaList, ShortLinkCreate,
                                ShortLinkToDBBase, ShortLinkUpdate, LinkType)
from services.helpers import id_generator, is_valid_url
from services.shortlink import short_link_crud, access_log_crud
from services.users import current_active_user

shorten_url_router = APIRouter()


@shorten_url_router.get('/ping')
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


@shorten_url_router.post('/',
                         response_model=ShortLinkSchemaCreate,
                         status_code=status.HTTP_201_CREATED
                         )
async def create_create_short_link(
        *,
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
        link: ShortLinkCreate,
) -> Any:
    """
    Create new short link
    """

    if not is_valid_url(link.original_url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This is not the URL')

    short_link = id_generator()

    new_link = ShortLinkToDBBase(
        short_url=short_link,
        original_url=link.original_url,
        owner_id=user.id if user else None,
        type=link.type if user else LinkType.PUBLIC.value
    )
    entity = await short_link_crud.create(db=db, obj_in=new_link)
    return entity


@shorten_url_router.get('/{short_url}', status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def redirect_to_link(
        *,
        db: AsyncSession = Depends(get_async_session),
        request: Request,
        user: User = Depends(current_active_user),
        short_url: str
) -> Any:
    """
    Redirect by short link
    """
    entity = await short_link_crud.get(db=db, short_url=short_url)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Item not found'
        )

    if not entity.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail='Item deleted'
        )

    if entity.type == 'private':
        if not user or user != entity.owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='You have not access'
            )

    history = str(jsonable_encoder(request.headers))

    access_log = AccessLogToDBBase(
        connection_info=history,
        short_link_id=entity.id
    )

    await access_log_crud.create(db=db, obj_in=access_log)

    return RedirectResponse(url=entity.original_url)


@shorten_url_router.get('/user/status', response_model=List[ShortLinkSchemaList])
async def user_status(
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
) -> Any:
    """
    Get the list of user's short links
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='You have not access'
        )

    short_links = await short_link_crud.get_multi(db=db, owner_id=user.id, is_active=True)

    return short_links


@shorten_url_router.delete('/{short_url}')
async def delete_link(
        *,
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
        short_url: str
) -> Any:
    """
    Delete short link
    """
    entity = await short_link_crud.get(db=db, short_url=short_url)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Item not found'
        )

    if not entity.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail='Item deleted'
        )

    if entity.owner:
        if not user or user != entity.owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='You have not access'
            )

    await short_link_crud.soft_delete(db=db, db_obj=entity)

    return {'success': True}


@shorten_url_router.put('/{short_url}',
                        response_model=ShortLinkSchemaList,
                        status_code=status.HTTP_202_ACCEPTED
                        )
async def update_link(
        *,
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
        short_url: str,
        type_data: ShortLinkUpdate
) -> Any:
    """
    Update short link. Only for registered user.
    """
    entity = await short_link_crud.get(db=db, short_url=short_url)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Item not found'
        )

    if not entity.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail='Item deleted'
        )

    if not user or user != entity.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='You have not access'
        )

    if type_data.type not in LinkType.items():
        acceptable_types = ', '.join(LinkType.items())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'You can choose only: {acceptable_types}'
        )

    await short_link_crud.update(db=db, db_obj=entity, obj_in=type_data)

    return entity


@shorten_url_router.get('/{short_url}/status', response_model=AccessLogStatistic)
async def get_link_statistic(
        *,
        full_info: str = None,
        offset: int = 0,
        limit: int = Query(10, alias='max-result'),
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
        short_url: str,
) -> Any:
    short_link = await short_link_crud.get(db=db, short_url=short_url)
    if not short_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Item not found'
        )

    if not short_link.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail='Item deleted'
        )

    if short_link.type == 'private':
        if not user or user != short_link.owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='You have not access'
            )

    access_logs_for_count = await access_log_crud.get_multi(
        db=db,
        short_link_id=short_link.id
    )

    access_log_statistic = AccessLogStatistic(
        requests_count=len(access_logs_for_count)
    )

    access_logs = await access_log_crud.get_multi(
        db=db,
        offset=offset,
        limit=limit,
        short_link_id=short_link.id
    )

    if isinstance(full_info, str):
        access_log_statistic.logs = access_logs

    return access_log_statistic

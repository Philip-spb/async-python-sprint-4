from typing import Any, List

import logging

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_async_session
from models.general import User
from schemas.access_log import AccessLogToDBBase, AccessLogStatistic
from schemas.short_link import (ShortLinkSchemaCreate, ShortLinkSchemaList, ShortLinkCreate,
                                ShortLinkToDBBase, ShortLinkUpdate, LinkType)
from services.helpers import id_generator, short_link_validation
from services.shortlink import short_link_crud, access_log_crud
from services.users import current_active_user


logger = logging.getLogger()
shorten_url_router = APIRouter()


@shorten_url_router.post('/',
                         response_model=ShortLinkSchemaCreate,
                         status_code=status.HTTP_201_CREATED
                         )
async def create_short_link(
        *,
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
        link: ShortLinkCreate,
) -> Any:
    """
    Create new short link
    """

    short_link = id_generator()

    new_link = ShortLinkToDBBase(
        short_url=short_link,
        original_url=link.original_url,
        owner_id=user.id if user else None,
        type=link.link_type if user else LinkType.PUBLIC.value
    )
    short_link = await short_link_crud.create(db=db, obj_in=new_link)
    return short_link


async def redirect_logging(db: AsyncSession, history: str, short_link_id: int):
    access_log = AccessLogToDBBase(
        connection_info=history,
        short_link_id=short_link_id
    )
    await access_log_crud.create(db=db, obj_in=access_log)


@shorten_url_router.get('/{short_url}', status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def redirect_to_link(
        *,
        db: AsyncSession = Depends(get_async_session),
        request: Request,
        background_tasks: BackgroundTasks,
        user: User = Depends(current_active_user),
        short_url: str
) -> Any:
    """
    Redirect by short link
    """
    short_link = await short_link_crud.get(db=db, short_url=short_url)

    short_link_validation(short_link)

    if short_link.link_type == 'private':
        if not user or user != short_link.owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='You have not access'
            )

    history = str(jsonable_encoder(request.headers))

    background_tasks.add_task(redirect_logging, db, history, short_link.id)

    logger.info(f'Redirect by the short link ({short_url}) to the url ({short_link.original_url})')

    return RedirectResponse(url=short_link.original_url)


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
    short_link = await short_link_crud.get(db=db, short_url=short_url)

    short_link_validation(short_link)

    if short_link.owner:
        if not user or user != short_link.owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='You have not access'
            )

    await short_link_crud.soft_delete(db=db, db_obj=short_link)

    logger.info(f'Deleted the short link ({short_url})')

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
    Update short link. Only for registered user and only for changing type parameter.
    """
    short_link = await short_link_crud.get(db=db, short_url=short_url)

    short_link_validation(short_link)

    if not user or user != short_link.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='You have not access'
        )

    if type_data.link_type not in LinkType.items():
        acceptable_types = ', '.join(LinkType.items())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'You can choose only: {acceptable_types}'
        )

    if type_data.link_type == short_link.link_type:
        logger.info(f'Nothing to change at the short link ({short_url})')
        return short_link

    await short_link_crud.update(db=db, db_obj=short_link, obj_in=type_data)

    logger.info(
        f'Has been edited the short link ({short_url}) privacy type to {type_data.link_type}'
    )

    return short_link


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
    """
    Get the history of short link usage.
    """
    short_link = await short_link_crud.get(db=db, short_url=short_url)

    short_link_validation(short_link)

    if short_link.link_type == 'private':
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

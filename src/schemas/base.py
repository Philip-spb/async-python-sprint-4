from uuid import UUID
from typing import Optional, Union, List
from datetime import datetime

from pydantic import BaseModel

from schemas.users import UserRead


class AccessLogRead(BaseModel):
    connection_info: str
    create_at: datetime

    class Config:
        orm_mode = True


class ShortLinkBase(BaseModel):
    original_url: str


class ShortLinkCreate(ShortLinkBase):
    ...


class ShortLinkUpdate(ShortLinkBase):
    ...


class ShortLinkToDBBase(ShortLinkBase):
    short_url: str
    original_url: str
    type: Optional[str] = 'public'
    owner_id: Optional[UUID]
    is_active: Optional[bool]


class ShortLinkInDBBase(ShortLinkBase):
    id: int
    short_url: str
    original_url: str
    type: str
    owner_id: Optional[UUID]
    owner: Union[UserRead, None] = None
    links: Union[List[AccessLogRead], None] = None
    is_active: Optional[bool]
    create_at: datetime

    class Config:
        orm_mode = True


# Properties to return to client
class ShortLinkShenma(ShortLinkInDBBase):
    pass


# Properties stored in DB
class ShortLinkInDB(ShortLinkInDBBase):
    pass

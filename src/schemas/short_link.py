from enum import Enum
from uuid import UUID
from typing import Optional, Dict, Literal
from pydantic import BaseModel, Field, root_validator, AnyUrl

from core import config


class LinkType(Enum):
    PRIVATE = 'private'
    PUBLIC = 'public'

    @classmethod
    def items(cls):
        return (i.value for i in cls)


class ShortLinkBase(BaseModel):
    original_url: AnyUrl = Field(alias='original-url')
    type: Literal[
        LinkType.PUBLIC.value,
        LinkType.PRIVATE.value
    ] = LinkType.PUBLIC.value

    class Config:
        allow_population_by_field_name = True


class ShortLinkCreate(ShortLinkBase):
    ...


class ShortLinkUpdate(BaseModel):
    type: Literal[
        LinkType.PUBLIC.value,
        LinkType.PRIVATE.value
    ] = LinkType.PUBLIC.value


class ShortLinkToDBBase(ShortLinkBase):
    short_url: str
    original_url: AnyUrl
    type: Optional[str] = LinkType.PUBLIC.value
    owner_id: Optional[UUID]
    is_active: Optional[bool]


class ShortLinkInDBBase(BaseModel):
    id: int = Field(alias='short-id')
    short_url: str = Field(alias='short-url')

    @root_validator
    def compute_area(cls, values) -> Dict:
        short_url = values.get('short_url')
        values['short_url'] = f'http://{config.PROJECT_HOST}:{config.PROJECT_PORT}/{short_url}'
        return values

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class ShortLinkSchemaCreate(ShortLinkInDBBase):
    pass


class ShortLinkSchemaList(ShortLinkInDBBase):
    original_url: AnyUrl = Field(alias='original-url')
    type: str


class ShortLinkInDB(ShortLinkInDBBase):
    pass

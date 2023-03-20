
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class AccessLogBase(BaseModel):
    connection_info: str
    create_at: datetime

    class Config:
        orm_mode = True


class AccessLogCreate(AccessLogBase):
    ...


class AccessLogUpdate(AccessLogBase):
    ...


class AccessLogToDBBase(BaseModel):
    connection_info: str
    short_link_id: int


class AccessLogStatistic(BaseModel):
    requests_count: int = 0
    logs: Optional[List[AccessLogBase]] = None

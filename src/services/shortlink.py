from models.general import ShortLink as ShortLinkModel, AccessLog as AccessLogModel
from schemas.access_log import AccessLogCreate, AccessLogUpdate
from schemas.short_link import ShortLinkCreate, ShortLinkUpdate
from services.base import RepositoryDB


class RepositoryShortLink(RepositoryDB[ShortLinkModel, ShortLinkCreate, ShortLinkUpdate]):
    pass


class RepositoryAccessLog(RepositoryDB[AccessLogModel, AccessLogCreate, AccessLogUpdate]):
    pass


short_link_crud = RepositoryShortLink(ShortLinkModel)
access_log_crud = RepositoryAccessLog(AccessLogModel)

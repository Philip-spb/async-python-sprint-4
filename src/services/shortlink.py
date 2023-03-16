from models.general import ShortLink as ShortLinkModel
from schemas.base import ShortLinkCreate, ShortLinkUpdate
from .base import RepositoryDB


class RepositoryEntity(RepositoryDB[ShortLinkModel, ShortLinkCreate, ShortLinkUpdate]):
    pass


short_link_crud = RepositoryEntity(ShortLinkModel)

import string
import random
from typing import Optional

from fastapi import HTTPException, status

from schemas.short_link import ShortLinkToDBBase


def id_generator(size: int = 6, chars=string.ascii_letters):
    return ''.join(random.choice(chars) for _ in range(size))


def short_link_validation(short_link: Optional[ShortLinkToDBBase]):
    if not short_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Item not found'
        )

    if not short_link.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail='Item deleted'
        )

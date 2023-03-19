import uvicorn
from fastapi import FastAPI, status, Response
from fastapi.responses import ORJSONResponse

from api.shorten_url import shorten_url_router
from core import config
from core.config import app_settings, BLACK_LIST
from api.v1 import base

app = FastAPI(
    title=app_settings.app_title,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.middleware("http")
async def check_client_ip(request, call_next):
    host = request.client.host

    if host in BLACK_LIST:
        return Response(status_code=status.HTTP_403_FORBIDDEN, content='Access denied')

    return await call_next(request)


app.include_router(base.api_router, prefix='/api/v1')
app.include_router(shorten_url_router, prefix='', tags=['main', ])

if __name__ == '__main__':
    uvicorn.run('main:app', host=config.PROJECT_HOST, port=config.PROJECT_PORT, reload=True,
                log_level='info')

# alembic -c src/alembic.ini current
# alembic -c src/alembic.ini revision --autogenerate -m 01_initial-db
# alembic -c src/alembic.ini upgrade head
# alembic -c src/alembic.ini downgrade -m e7515b7120ac_02_add_short_link_model
# alembic -c src/alembic.ini downgrade -1

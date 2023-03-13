import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from core import config
from core.config import app_settings
from api.v1 import base

app = FastAPI(
    title=app_settings.app_title,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(base.api_router, prefix='/api/v1')

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=config.PROJECT_HOST,
        port=config.PROJECT_PORT,
        reload=True,
        log_level='info'
    )

# alembic -c src/alembic.ini current
# alembic -c src/alembic.ini revision --autogenerate -m 01_initial-db
# alembic -c src/alembic.ini upgrade head

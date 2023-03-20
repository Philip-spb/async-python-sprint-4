import uvicorn
from fastapi import FastAPI, status, Response
from fastapi.responses import ORJSONResponse

from api.shorten_url import shorten_url_router
from core.config import app_settings
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

    if host in app_settings.black_list:
        return Response(status_code=status.HTTP_403_FORBIDDEN, content='Access denied')

    return await call_next(request)


app.include_router(base.api_router, prefix='/api/v1')
app.include_router(shorten_url_router, prefix='', tags=['main', ])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_settings.project_host,
        port=app_settings.project_port,
        reload=True,
        log_level='info'
    )

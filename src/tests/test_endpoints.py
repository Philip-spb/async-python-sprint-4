import json
from fastapi import status
from httpx import AsyncClient

from main import app
from schemas.short_link import ShortLinkSchemaCreate


async def test_access_from_forbidden_ip(mocker, event_loop):
    mock_client = mocker.patch('fastapi.Request.client')
    mock_client.host = '56.24.15.106'
    async with AsyncClient(app=app, base_url='http://test') as ac:
        response = await ac.get(app.url_path_for('ping_db'))
        assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_access_from_allowed_ip(mocker, event_loop):
    mock_client = mocker.patch('fastapi.Request.client')
    mock_client.host = '192.168.1.1'
    async with AsyncClient(app=app, base_url='http://test') as ac:
        response = await ac.get(app.url_path_for('ping_db'))
        assert response.status_code == status.HTTP_200_OK


async def test_create_user(event_loop):
    user_data = {
        "email": 'homer@simpson.com',
        "password": 'springfield',
    }
    async with AsyncClient(app=app, base_url='http://test') as ac:
        response = await ac.post(app.url_path_for('register:register'), json=user_data)
        assert response.status_code == status.HTTP_201_CREATED


async def test_create_and_delete_shortlink(event_loop):
    link = {'original-url': 'http://www.ya.ru'}
    async with AsyncClient(app=app, base_url='http://test') as ac:
        response = await ac.post(app.url_path_for('create_short_link'), json=link)
        assert response.status_code == status.HTTP_201_CREATED
        data = ShortLinkSchemaCreate.parse_obj(json.loads(response.content.decode()))
        short_url = data.short_url.split('/')[-1]
        response = await ac.delete(f'/{short_url}')
        assert response.status_code == status.HTTP_200_OK

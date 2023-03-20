from fastapi import status
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_access_from_forbidden_ip(mocker):
    mock_client = mocker.patch('fastapi.Request.client')
    mock_client.host = '56.24.15.106'
    response = client.get(app.url_path_for('ping_db'))
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_access_from_allowed_ip(mocker):
    mock_client = mocker.patch('fastapi.Request.client')
    mock_client.host = '192.168.1.1'
    response = client.get(app.url_path_for('ping_db'))
    assert response.status_code == status.HTTP_200_OK

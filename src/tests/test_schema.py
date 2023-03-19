import pytest
from pydantic import ValidationError

from fastapi import status
from fastapi.testclient import TestClient

from main import app
from schemas.short_link import ShortLinkBase, ShortLinkUpdate


client = TestClient(app)


def test_access_from_forbidden_ip(mocker):
    mock_client = mocker.patch('fastapi.Request.client')
    mock_client.host = '56.24.15.106'
    response = client.get('/ping')
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_access_from_allowed_ip(mocker):
    mock_client = mocker.patch('fastapi.Request.client')
    mock_client.host = '192.168.1.1'
    response = client.get('/ping')
    assert response.status_code == status.HTTP_200_OK


def test_correct_create_link_schema():
    ShortLinkBase.parse_obj(
        {
            "original-url": "https://google.com",
            "type": "public"
        }
    )
    assert True


def test_incorrect_create_link_schema_1():
    with pytest.raises(ValidationError):
        ShortLinkBase.parse_obj(
            {
                "original-url": "google.com",
                "type": "public"
            }
        )
    assert True


def test_incorrect_create_link_schema_2():
    with pytest.raises(ValidationError):
        ShortLinkBase.parse_obj(
            {
                "original-url": "http://google.com",
                "type": "public2"
            }
        )
    assert True


def test_correct_update_link_schema():
    ShortLinkUpdate.parse_obj(
        {
            "type": "public"
        }
    )
    assert True


def test_incorrect_update_link_schema():
    with pytest.raises(ValidationError):
        ShortLinkUpdate.parse_obj(
            {
                "type": "public1"
            }
        )
    assert True

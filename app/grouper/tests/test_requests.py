import pytest
from faker import Faker
from fastapi import FastAPI
from httpx import AsyncClient
from redis import Redis
from starlette.status import (
    HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_201_CREATED)


faker = Faker()


class TestRoutes:
    @pytest.mark.endpoint_request
    @pytest.mark.asyncio
    async def test_grouping_route_exist(self, app: FastAPI, client: AsyncClient) -> None:
        response = await client.post(app.url_path_for('add-to-groups'), json={})
        assert response.status_code != HTTP_404_NOT_FOUND

    @pytest.mark.endpoint_request
    @pytest.mark.asyncio
    async def test_grouping_request_json_content(self, app: FastAPI, client: AsyncClient) -> None:
        response = await client.post(app.url_path_for('add-to-groups'))
        assert response.status_code == HTTP_400_BAD_REQUEST

    @pytest.mark.endpoint_request
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'text',
        [faker.catch_phrase() for _ in range(10)]
    )
    async def test_grouping_success_request(self, app: FastAPI, client: AsyncClient, text: str) -> None:
        response = await client.post(app.url_path_for('add-to-groups'), json={'articles': [text]})
        assert response.status_code == HTTP_201_CREATED

    @pytest.mark.endpoint_request
    @pytest.mark.asyncio
    async def test_empty_json_raises_error(self, app: FastAPI, client: AsyncClient) -> None:
        response = await client.post(app.url_path_for('add-to-groups'), json={})
        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.endpoint_request
    @pytest.mark.asyncio
    async def test_clean_db_route_exist(self, app: FastAPI, client: AsyncClient) -> None:
        response = await client.post(app.url_path_for('clean-db'))
        assert response.status_code != HTTP_404_NOT_FOUND

    @pytest.mark.endpoint_request
    @pytest.mark.asyncio
    async def test_clean_db_deletion(self, app: FastAPI, client: AsyncClient, redis_conn: Redis):
        redis_conn.append('test', 'true')
        await client.post(app.url_path_for('clean-db'))
        assert not redis_conn.keys()

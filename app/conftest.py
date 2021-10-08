import logging

import pytest
import redis
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient

from grouper.settings import REDIS_HOST, REDIS_PORT


logger = logging.getLogger(__name__)


@pytest.fixture
def app() -> FastAPI:
    from grouper.main import application

    return application


@pytest.fixture
async def client(app: FastAPI):
    async with LifespanManager(app):
        async with AsyncClient(
            app=app,
            base_url="http://localhost",
            headers={"Content-Type": "application/json"}
        ) as client:
            yield client


@pytest.fixture
def redis_conn():
    conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    yield conn
    conn.flushall()


@pytest.fixture(scope='session')
def stopwords():
    try:
        with open('stopwords/russian1') as file:
            return file.read().splitlines()
    except FileNotFoundError as e:
        logger.warning(str(e))
        return []

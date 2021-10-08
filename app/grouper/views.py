import logging
from json import JSONDecodeError

from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from pydantic import ValidationError
from redis import RedisError

from grouper.models import ArticlesInRequest
from services.grouper import get_groups


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post('/', name='add-to-groups', status_code=201)
async def add_to_groups(request: Request) -> dict:
    try:
        json_data = await request.json()
    except JSONDecodeError:
        raise HTTPException(status_code=400, detail='Must provide JSON data in request.')

    try:
        articles = ArticlesInRequest(articles=json_data.get('articles'))
    except ValidationError as e:
        msg = str(e)
        logger.debug(msg)
        raise HTTPException(status_code=422, detail=msg)

    groups = await get_groups(articles.articles)

    return {'groups': groups}


@router.post('/clean-db', name='clean-db')
async def clean_db(request: Request) -> dict:
    try:
        request.app.state.storage.flushall()
    except RedisError as e:
        msg = str(e)
        logger.debug(msg)
        raise HTTPException(status_code=500, detail=msg)

    return {'status': 'success'}

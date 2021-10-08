import logging
from json import JSONDecodeError

from fastapi import APIRouter
from fastapi.requests import Request
from pydantic import ValidationError
from redis import RedisError

from grouper.models import ArticlesInRequest
from services.grouper import get_groups, redis_instance


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post('/', name='add-to-groups')
async def add_to_groups(request: Request) -> dict:
    try:
        json_data = await request.json()
    except JSONDecodeError:
        return {'error': 'Must provide JSON data in request.'}

    try:
        articles = ArticlesInRequest(articles=json_data.get('articles'))
    except ValidationError as e:
        return {'error': str(e)}

    groups = await get_groups(articles.articles)

    return {'groups': groups}


@router.post('/clean-db', name='clean-db')
async def clean_db(request: Request) -> dict:
    try:
        redis_instance.flushall()
    except RedisError as e:
        logger.error(str(e))

        return {'status': 'error'}

    return {'status': 'success'}

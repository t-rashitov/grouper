import logging

from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from redis import RedisError

from grouper.models import ArticlesInRequest
from services.grouper import get_groups


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post('/', name='add-to-groups', status_code=200)
async def add_to_groups(articles_data: ArticlesInRequest) -> dict:
    """Группировка текстов по группам"""

    groups = await get_groups(articles_data.articles)

    return {'groups': groups}


@router.post('/clean-db', name='clean-db')
async def clean_db(request: Request) -> dict:
    """Очистка хранилища (redis) хешей (minhash)"""

    try:
        request.app.state.storage.flushall()
    except RedisError as e:
        msg = str(e)
        logger.debug(msg)

        raise HTTPException(status_code=500, detail=msg)

    return {'status': 'success'}

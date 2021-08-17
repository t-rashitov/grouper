from json import JSONDecodeError

from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from pydantic import ValidationError

from app.grouper.models import ArticlesInRequest
from app.services.grouper import get_groups


async def add_to_groups(request: Request):
    try:
        json_data = await request.json()
    except JSONDecodeError:
        return json_response({'error': 'Must provide JSON data in request.'})

    try:
        articles = ArticlesInRequest(articles=json_data.get('articles'))
    except ValidationError as e:
        return json_response({'error': str(e)})

    groups = await get_groups(articles.articles)

    return json_response({'groups': groups})

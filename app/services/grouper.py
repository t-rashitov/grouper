import asyncio
import logging
import os
import pathlib
import re
import uuid
from datetime import datetime

import uvloop
from datasketch import MinHash, MinHashLSH
from pymorphy2 import MorphAnalyzer

from app.datasketch.experimental.aio.lsh import AsyncMinHashLSH

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BASE_DIR = pathlib.Path(__file__).parent.parent

try:
    russian_stopwords = tuple(open(os.path.join(BASE_DIR, 'stopwords/russian')).read().splitlines())
except FileNotFoundError:
    russian_stopwords = ()

morph_analyzer = MorphAnalyzer()


async def get_mongo_lsh() -> AsyncMinHashLSH:

    return await AsyncMinHashLSH(threshold=0.1, weights=(0.8, 0.2), num_perm=128, storage_config={
        'type': 'aiomongo',
        'mongo': {'host': 'localhost', 'port': 27017, 'db': 'local'}
    })


def get_redis() -> MinHashLSH:

    return MinHashLSH(threshold=0.1, weights=(0.8, 0.2), num_perm=256, storage_config={
        'type': 'redis',
        'redis': {'host': 'localhost', 'port': 6379},
    })


loop = asyncio.get_event_loop()
lsh = loop.run_until_complete(get_mongo_lsh())


async def parse_articles(articles: list) -> list:
    """
    Функция для предобработки текстов (удаление стопслов, знаков препинания, лемматизация)
    :param articles: список новостных статей
    :return parsed_articles: список предобработанных статей
    """

    parsed_articles = []

    for i, article in enumerate(articles, start=1):
        article = article.strip().lower().replace('ё', 'е')

        words_list = re.findall('\\w+', article, flags=re.IGNORECASE or re.MULTILINE)

        prepared_words = []

        for word in words_list:

            if word not in russian_stopwords:

                if len(word) > 1:
                    try:
                        prepared_words.append(morph_analyzer.parse(word)[0].normal_form)
                    except (AttributeError, IndexError):
                        logger.warning(f"Word <{word}> hasn't been changed.")
                        prepared_words.append(word)

                else:
                    prepared_words.append(word)

        if len(prepared_words) == 0:
            continue

        words_line = ' '.join(prepared_words)

        parsed_articles.append(words_line + '\n')

    return parsed_articles


async def parse_from_file(input_file_path: str, output_file_path: str):
    """
    Функция для обработки текстов из файла
    :param input_file_path: путь до входящего файла со статьями
    :param output_file_path: путь до исходящего файла со статьями
    :return:
    """

    file = open(input_file_path)

    try:
        articles = file.readlines()
    finally:
        file.close()

    logger.debug(f'articles count: {len(articles)}')

    parsed_articles = await parse_articles(articles)

    with open(output_file_path, 'w') as file:
        file.writelines(parsed_articles)

    logger.debug(f'parsed articles count: {len(parsed_articles)}')

    return parsed_articles


async def get_groups(raw_articles: list[str]) -> list:
    """
    Функция возвращает uuid группы к которой может относиться текст или создание новую группу
    :param raw_articles: список статей
    :return:
    """

    articles = await parse_articles(raw_articles)

    groups = []

    for i, article in enumerate(articles):
        article_set = set([word.encode('utf-8') for word in article.split(' ')])
        # article_set = [word.encode('utf-8') for word in article.split(' ')]
        min_hash = MinHash(num_perm=128)
        min_hash.update_batch(list(article_set))
        # min_hash.update_batch(article_set)

        results = await lsh.query(min_hash)

        if not results:
            uid = uuid.uuid1()
            timestamp = datetime.now().timestamp()
            await lsh.insert(f'{uid}_{timestamp}', min_hash)
            groups.append(str(uid))
            continue

        result_by_groups = {}
        for result in results:
            result_uuid = result.split('_')[0]
            result_by_groups[result_uuid] = result_by_groups.get(result_uuid, 0) + 1

        groups.append(max(result_by_groups, key=result_by_groups.get))

    return groups

import logging
import os
import pathlib
import re
import uuid
from datetime import datetime

from datasketch import MinHash, MinHashLSH
from pymorphy2 import MorphAnalyzer

from grouper.settings import REDIS_HOST, REDIS_PORT

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BASE_DIR = pathlib.Path(__file__).parent.parent

try:
    russian_stopwords = tuple(open(os.path.join(BASE_DIR, 'stopwords/russian')).read().splitlines())
except FileNotFoundError:
    russian_stopwords = ()

morph_analyzer = MorphAnalyzer()


def get_redis() -> MinHashLSH:

    return MinHashLSH(threshold=0.25, weights=(.85, .15), num_perm=256, storage_config={
        'type': 'redis',
        'redis': {'host': REDIS_HOST, 'port': REDIS_PORT},
    })


lsh = get_redis()


async def parse_articles(articles: list) -> list:
    """
    Функция для предобработки текстов (удаление стопслов, знаков препинания, лемматизация)
    :param articles: список новостных статей
    :return parsed_articles: список предобработанных статей
    """

    parsed_articles = []

    for article in articles:
        article = article.strip().lower()

        words_list = re.findall('\\w+', article, flags=re.IGNORECASE or re.MULTILINE)

        prepared_words = []

        for word in words_list:

            if word not in russian_stopwords:

                if len(word) > 1:
                    try:
                        prepared_words.append(morph_analyzer.parse(word)[0].normal_form)
                    except (AttributeError, IndexError):
                        logger.warning(f'Word <{word}> hasn\'t been changed.')
                        prepared_words.append(word)

                else:
                    prepared_words.append(word)

        if len(prepared_words) == 0:
            continue

        words_line = ' '.join(prepared_words)

        parsed_articles.append(words_line)

    return parsed_articles


async def parse_from_file(input_file_path: str, output_file_path: str):
    """
    Функция для обработки текстов из файла
    :param input_file_path: путь до входящего файла со статьями
    :param output_file_path: путь до исходящего файла со статьями
    :return:
    """

    with open(input_file_path) as file:
        articles = file.readlines()

    logger.debug(f'articles count: {len(articles)}')

    parsed_articles = await parse_articles(articles)

    with open(output_file_path, 'w') as file:
        file.writelines([article + '\n' for article in parsed_articles])

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
        article_set = [word.encode('utf-8') for word in article.split(' ')]
        min_hash = MinHash(num_perm=256)
        min_hash.update_batch(article_set)

        results = lsh.query(min_hash)

        ts = datetime.now().timestamp()

        if not results:
            uid = uuid.uuid1()
            lsh.insert(f'{uid}_{ts}', min_hash)
            groups.append(str(uid))

            continue

        result_by_groups = {}
        for result in results:
            result_uuid = result.split('_')[0]
            result_by_groups[result_uuid] = result_by_groups.get(result_uuid, 0) + 1

        result = max(result_by_groups, key=result_by_groups.get)
        lsh.insert(f'{result}_{ts}', min_hash)
        groups.append(result)

    return groups

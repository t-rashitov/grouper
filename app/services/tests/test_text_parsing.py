import os

import pytest
from faker import Faker

from services.grouper import parse_articles


faker = Faker()


@pytest.mark.parsing
def test_stopwords_exist():
    assert os.path.isfile('stopwords/russian')


@pytest.mark.parsing
@pytest.mark.asyncio
async def test_stop_word_deletion(stopwords: list):

    stopwords_line = ' '.join(stopwords)

    parsed_line = await parse_articles([stopwords_line])

    assert parsed_line == []


@pytest.mark.parametrize(
    'line',
    [' '.join(faker.color_name() for _ in range(10)) for _ in range(10)]
)
@pytest.mark.parsing
@pytest.mark.asyncio
async def test_parsed_articles_words_count(line):
    articles = await parse_articles([line])

    assert len(articles[0].split()) == 10


@pytest.mark.parsing
@pytest.mark.asyncio
async def test_word_normalization():
    article = ('Марс — четвёртая по удалённости от Солнца (после Меркурия, Венеры и Земли) и седьмая по размеру '
               '(превосходит по массе и диаметру только Меркурий) планета Солнечной системы[11]. Масса Марса '
               'составляет 0,107 массы Земли, объём — 0,151 объёма Земли, а средний линейный диаметр — 0,53 диаметра '
               'Земли')

    parsed = await parse_articles([article])

    assert parsed[0] == ('марс четвёртый удалённость солнце меркурий венера земля седьмой размер превосходить масса '
                         'диаметр меркурий планета солнечный система 11 масса марс составлять 0 107 масса земля объём '
                         '0 151 объём земля средний линейный диаметр 0 53 диаметр земля')

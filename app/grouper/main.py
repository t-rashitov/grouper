import logging
import sys

from aiohttp import web

from app.grouper.routes import setup_routers
from app.grouper.settings import get_config


def get_app(argv=None):
    app = web.Application()
    app['config'] = get_config(argv)

    setup_routers(app)

    return app


def main(argv):
    logging.basicConfig(level=logging.DEBUG)

    app = get_app(argv)

    config = get_config(argv)
    web.run_app(app, host=config['host'], port=config['port'])


if __name__ == '__main__':
    main(sys.argv[1:])


# TODO: Добавить удаление записей из БД по истечению 2-3 дней
# TODO: Провести нагрузочное тестирование
# TODO: Сравнить результат с сервисом на Flask + Redis

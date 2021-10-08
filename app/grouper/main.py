import logging
import sys

import redis
import uvicorn
from fastapi import FastAPI

from grouper.settings import get_config, REDIS_HOST, REDIS_PORT
from grouper.views import router


def get_application() -> FastAPI:
    app = FastAPI()
    app.state.storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    app.include_router(router)

    return app


application = get_application()


def main(argv):
    logging.basicConfig(level=logging.DEBUG)

    config = get_config(argv)
    uvicorn.run('grouper.main:application', host=config['host'], port=config['port'], workers=config['workers'])


if __name__ == '__main__':
    main(sys.argv[1:])

import logging
import sys

import uvicorn
from fastapi import FastAPI

from grouper.settings import get_config
from grouper.views import router


def get_application() -> FastAPI:
    app = FastAPI()
    app.include_router(router)

    return app


application = get_application()


def main(argv):
    logging.basicConfig(level=logging.DEBUG)

    config = get_config(argv)
    uvicorn.run('grouper.main:application', host=config['host'], port=config['port'], workers=config['workers'])


if __name__ == '__main__':
    main(sys.argv[1:])

from aiohttp.web import Application

from app.grouper.views import add_to_groups


def setup_routers(app: Application) -> None:
    app.router.add_post('/', add_to_groups, name='add')

from pydantic.main import BaseModel


class ArticlesInRequest(BaseModel):
    articles: list[str]

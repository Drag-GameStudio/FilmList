from pydantic import BaseModel


class Review(BaseModel):
    film_id: int
    user_id: int
    content: str
    rate: int


class ReviewSearchingParams(BaseModel):
    review_id: int | None = None
    film_id: int | None = None
    user_id: int | None = None
    content: str | None = None
    rate: int | None = None

class ReviewForAdd(BaseModel):
    film_id: int
    content: str
    rate: int


class FilmBase(BaseModel):
    id: int
    image: str
    title: str


class FilmBaseSearchingParams(BaseModel):
    id: int | None = None
    image: str | None = None
    title: str | None = None
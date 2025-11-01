from pydantic import BaseModel


class FilmInfo(BaseModel):
    id: int
    image: str
    title: str

class FilmSerchingParams(BaseModel):
    id: int | None = None
    image: str | None = None
    title: str | None = None

class FilmCreator(BaseModel):
    id: int

class WishListFilmAdd(BaseModel):
    id: int
    user_id: int



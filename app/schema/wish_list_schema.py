from pydantic import BaseModel


class WishListCreator(BaseModel):
    user_id: int

class AddToWishList(BaseModel):
    user_id: int
    film_id: int

class UpdateWishList(BaseModel):
    films: list[int]
from app.repositories.base_repository import BaseRepository
from app.models.film import FilmReview



class FilmReviewRepository(BaseRepository):
    def __init__(self, session_factory):
        super().__init__(session_factory, FilmReview)
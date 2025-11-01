from app.repositories.review_repository import FilmReviewRepository
from app.schema.film_review import Review, FilmBaseSearchingParams, ReviewSearchingParams
from app.services.film_service import FilmService, FilmRepository


class ReviewService():
    def __init__(self, film_review_repository: FilmReviewRepository):
        self.film_review_repository = film_review_repository
        self.film_service = FilmService(FilmRepository(film_review_repository.session_factory))

    def add_review(self, review_info: Review):
        status, film_object = self.film_service.get_info_about_film(FilmBaseSearchingParams(id=review_info.film_id))
        if status == False:
            return False, None
        status, review_object = self.film_review_repository.create(review_info)

        return status, review_object
    
    def get_reviews(self, review_info: ReviewSearchingParams): 
        reviews_objects = self.film_review_repository.read_by_options(review_info).get("all")
        return reviews_objects
    
    def delete_review(self, review_info: ReviewSearchingParams):
        status = self.film_review_repository.delete_object(review_info)
        return status



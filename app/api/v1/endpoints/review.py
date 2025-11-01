from fastapi import APIRouter, Depends
from app.core.dependencies import verify_user
from app.services.review_service import ReviewService, FilmReviewRepository
from app.schema.film_review import Review, ReviewForAdd, ReviewSearchingParams
from app.db.database import SessionLocal


router = APIRouter(
    prefix="/review",
    tags=["review"]
)



@router.post("/{film_id}")
def add_review(review_info: ReviewForAdd, verify_data = Depends(verify_user)):
    message = verify_data["message"]


    if verify_data["status"]:
        review_service_object = ReviewService(FilmReviewRepository(SessionLocal))
        status, review_object = review_service_object.add_review(Review(
            film_id=review_info.film_id,
            user_id=verify_data["user_id"],
            content=review_info.content,
            rate=review_info.rate
            ))

        if status:
            return {"status": "success", "result": review_object}

        return {"status": "error", "message": message}


@router.get("/")
def get_reviews(filters: ReviewSearchingParams = Depends(), verify_data = Depends(verify_user)):
    message = verify_data["message"]

    if verify_data["status"]:
        review_service_object = ReviewService(FilmReviewRepository(SessionLocal))
        reviews = review_service_object.get_reviews(filters)

        return {"status": "success", "result":  reviews}

    return {"status": "error", "message": message}



@router.get("/my")
def get_my_reviews(verify_data = Depends(verify_user)):
    message = verify_data["message"]

    if verify_data["status"]:
        review_service_object = ReviewService(FilmReviewRepository(SessionLocal))
        reviews = review_service_object.get_reviews(ReviewSearchingParams(user_id=verify_data["user_id"]))

        return {"status": "success", "results":  reviews}

    return {"status": "error", "message": message}



@router.delete("/{review_id}")
def delete_review(review_id: int, verify_data = Depends(verify_user)):
    message = verify_data["message"]

    if verify_data["status"]:
        review_service_object = ReviewService(FilmReviewRepository(SessionLocal))
        status = review_service_object.delete_review(ReviewSearchingParams(review_id=review_id, user_id=verify_data["user_id"]))
        if status:
            return {"status": "success"}
        
    return {"status": "error", "message": message}

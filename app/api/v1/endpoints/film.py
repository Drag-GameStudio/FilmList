from fastapi import APIRouter, Depends
from app.db.database import SessionLocal
from app.services import film_service, wish_list_service
from app.repositories.film_repository import FilmRepository
from app.repositories.wish_list_repository import WishListRepository
from app.core.dependencies import verify_user
from app.schema.film_schema import FilmSerchingParams
from app.schema.wish_list_schema import AddToWishList, WishListCreator


router = APIRouter(
    prefix="/film",
    tags=["film"]
)


@router.get("/search_film")
def search_film(query: str, verify_data = Depends(verify_user)):
    message = verify_data["message"]
    if verify_data["status"]:
        film_service_object = film_service.FilmService(FilmRepository(SessionLocal))
        films = film_service_object.find_film_by_name(q=query)
        return{"status": "success", "result": films}
    
    return {"status": "error", "message": message}

@router.post("/wish_list/{film_id}")
def add_film_to_wish_list(film_id: int, verify_data = Depends(verify_user)):
    message = verify_data["message"]
    if verify_data["status"]:
        wish_list_service_object = wish_list_service.WishListService(WishListRepository(SessionLocal))
        status, wish_list = wish_list_service_object.add_film_to_wish_list(AddToWishList(user_id=verify_data["user_id"], film_id=film_id))

        if status:
            return {"status": "success", "result": wish_list}
        
        message = "This film id is non-existent"

    return {"status": "error", "message": message}

@router.delete("/wish_list/{film_id}")
def del_film_from_wish_list(film_id: int, verify_data = Depends(verify_user)):
    message = verify_data["message"]
    if verify_data["status"]:
        wish_list_service_object = wish_list_service.WishListService(WishListRepository(SessionLocal))
        status, wish_list = wish_list_service_object.remove_film_from_wish_list(AddToWishList(user_id=verify_data["user_id"], film_id=film_id))

        if status:
            return {"status": "success"}
        
        message = "This film hasnt been existed"
        
    return {"status": "error", "message": message}

@router.get("/wish_list")
def get_wish_list(verify_data = Depends(verify_user)):
    message = verify_data["message"]
    if verify_data["status"]:
        wish_list_service_object = wish_list_service.WishListService(WishListRepository(SessionLocal))

        status, wish_list = wish_list_service_object.get_wish_list(WishListCreator(user_id=verify_data["user_id"]))
        if status:
            wish_list.reverse()
            return {"status": "success", "result": wish_list}
        
        message = "Something happend"

    return {"status": "error", "message": message}


@router.get("/{film_id}")
def get_info_about_film(film_id: int, verify_data = Depends(verify_user)):
    message = verify_data["message"]
    if verify_data["status"]:
        film_service_object = film_service.FilmService(FilmRepository(SessionLocal))
        status, film_object = film_service_object.get_info_about_film(FilmSerchingParams(id=film_id))
        if status:
            return {"status": "success", "result": film_object}
        
        message = "This film id is non-existent"

    return {"status": "error", "message": message}


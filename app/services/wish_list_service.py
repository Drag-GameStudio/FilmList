from app.repositories.wish_list_repository import WishListRepository
from app.schema.wish_list_schema import WishListCreator, AddToWishList, UpdateWishList
from app.services.film_service import FilmRepository, FilmService
from app.schema.film_schema import FilmSerchingParams

class WishListService:
    def __init__(self, wish_list_repository: WishListRepository):
        self.wish_list_repository = wish_list_repository
        self.film_service = FilmService(FilmRepository(self.wish_list_repository.session_factory))

    def create_wish_list(self, wish_list_creator: WishListCreator):
        status, wish_list_object = self.wish_list_repository.create(wish_list_creator)
        return status, wish_list_object
    
    def auto_create_wish_list(self, wish_list_creator: WishListCreator):
        status, wish_list_object = self.create_wish_list(wish_list_creator)
        if status:
            return True, wish_list_object
        
        wish_list_object = self.wish_list_repository.read_by_id(wish_list_creator)
        if wish_list_object is None:
            return False, None
        
        return True, wish_list_object
    
    def add_film_to_wish_list(self, add_info: AddToWishList):
        status, film_object = self.film_service.auto_create_film(FilmSerchingParams(id=add_info.film_id))
        if status == False:
            return False, None
        
        status, wish_list_object = self.auto_create_wish_list(WishListCreator(user_id=add_info.user_id))
        if status == False:
            return False, None
        

        update_film_list: list[int] = wish_list_object.get_films()

        update_film_list.append(film_object.id)

        update_film_list = list(set(update_film_list))

        wish_list_update = self.wish_list_repository.update_element_films(WishListCreator(user_id=add_info.user_id), UpdateWishList(films=update_film_list))

        return True, wish_list_update
        
    def remove_film_from_wish_list(self, remove_info: AddToWishList):
        status, wish_list_object = self.auto_create_wish_list(WishListCreator(user_id=remove_info.user_id))
        if status == False:
            return False, None
        update_film_list: list[int] = wish_list_object.get_films()
        update_film_list.remove(remove_info.film_id)
        wish_list_update = self.wish_list_repository.update_element_films(WishListCreator(user_id=remove_info.user_id), UpdateWishList(films=update_film_list))

        return True, wish_list_update
    
    def get_wish_list(self, wish_list_info: WishListCreator):
        status, wish_list_object = self.auto_create_wish_list(WishListCreator(user_id=wish_list_info.user_id))
        if status == False:
            return False, None
        
        return True, wish_list_object.films

        
        


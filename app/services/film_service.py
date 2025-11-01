from app.repositories.film_repository import FilmRepository
from app.side_api.tmdb_api import TMDB
from app.schema.film_schema import FilmInfo, FilmCreator, FilmSerchingParams


class FilmService:
    def __init__(self, film_repository: FilmRepository):
        self.film_repository = film_repository
        self.tmdb = TMDB()

    def find_film_by_name(self, q):
        films: list[FilmInfo] = self.tmdb.find_the_films(q)
        return films[:10]
    

    def auto_create_film(self, film_info: FilmSerchingParams):
        status, film_object = self.get_film(film_info=film_info)
        if status:
            return True, film_object
        
        status, film_object = self.create_film(FilmCreator(id=film_info.id))

        if status:
            return True, film_object
        
        return False, None

    def get_info_about_film(self, film_info: FilmSerchingParams):
        status, film_object = self.auto_create_film(film_info)
        if status:
            return True, film_object
        return False, None

    def get_film(self, film_info: FilmSerchingParams):
        curr_film = self.film_repository.read_by_id(film_info)
        if curr_film is None:
            return False, None
        
        return True, curr_film
    
    
    def create_film(self, film_creator: FilmCreator):

        info: FilmInfo = self.tmdb.find_film_by_id(film_creator.id)
        if info is None:
            return False, None

        status, film_object = self.film_repository.create(info)

        return status, film_object
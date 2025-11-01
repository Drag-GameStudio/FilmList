import requests
from app.schema.film_schema import FilmInfo
from app.core.config import settings

class Movie:
    def __init__(self, data: dict):
        self.data = data

    @property
    def title(self):
        return self.data["original_title"]
    
    @property
    def image(self):
        return f"https://image.tmdb.org/t/p/w500{self.data["poster_path"]}"
    
    @property
    def id(self):
        return self.data["id"]

    def __repr__(self):
        return f"{self.title}: {self.id}, {self.image}"
    
    @property
    def schema(self):
        return FilmInfo(id=self.id, image=self.image, title=self.title)

class TMDB:
    def __init__(self, api_key: str = settings.TMDB_API_KEY):
        self.api_key = api_key

    def find_the_films(self, q: str):
        url = f"https://api.themoviedb.org/3/search/movie"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        params = {
            "query": q,
            "language": "ru-RU"
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        return [Movie(el).schema for el in data["results"]]


    def find_film_by_id(self, film_id):

        url = f"https://api.themoviedb.org/3/movie/{film_id}"


        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        params = {
            "language": "ru-RU"
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        try:
            return Movie(data).schema
        
        except:
            return None



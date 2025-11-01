from app.repositories.base_repository import BaseRepository, Session
from app.models.film import WishList, Film


class WishListRepository(BaseRepository):
    def __init__(self, session_factory):
        super().__init__(session_factory, WishList)

    def update_element_films(self, schema_id, update_schema):
        session: Session = self.get_session()
        curr_object = self.read_by_id(schema_id)
        if curr_object is None:
            return None

        filled_schema_dict = update_schema.model_dump()

        for key, value in filled_schema_dict.items():
            # Если это поле films — нужно превратить список ID в объекты Film
            if key == "films":
                value = session.query(Film).filter(Film.id.in_(value)).all()
            setattr(curr_object, key, value)

        try:
            session.commit()
            session.refresh(curr_object)
        except Exception as e:
            session.rollback()
            return False, None

        return True, curr_object
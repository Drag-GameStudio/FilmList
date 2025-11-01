from app.repositories.base_repository import BaseRepository
from app.models.user import User, Session


class UserRepository(BaseRepository):
    def __init__(self, session_factory):
        super().__init__(session_factory, User)

class SessionRepository(BaseRepository):
    def __init__(self, session_factory):
        super().__init__(session_factory, Session)


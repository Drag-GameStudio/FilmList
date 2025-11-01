from app.repositories.user_repository import UserRepository, SessionRepository
from app.schema.auth_schema import UserInfo, UserSearchingParams, SessionInfo, SessionSearchingParams
from app.models.user import User, Session


class AuthService():
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.session_repository = SessionRepository(user_repository.session_factory)


    def regist(self, user: UserInfo):
        return self.user_repository.create(user)

    def login(self, user: UserInfo):
        curr_user: User = self.user_repository.read_by_id(UserSearchingParams(username=user.username))
        if curr_user is None:
            return False, "user hasnt been existed"
        
        password_check = curr_user.check_password(user.password)
        if password_check == False:
            return False, "incorrect password"
        
        status, created_session = self.session_repository.create(SessionInfo(user_id=curr_user.id))
        
        return status, created_session.id
    
    def logout(self, session_schema: SessionSearchingParams):
        status = self.session_repository.delete_object(session_schema)
        return status

    def check_auth(self, session_schema: SessionSearchingParams):
        curr_session: Session = self.session_repository.read_by_id(schema=session_schema)
        if curr_session is None:
            return False, None
        
        
        return True, curr_session.user.id
        

        
        

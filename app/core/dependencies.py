from fastapi import APIRouter, Depends, Response, Cookie
from app.schema.auth_schema import UserInfo, UserSearchingParams, SessionSearchingParams
from app.db.database import get_db, SessionLocal

from app.services import auth_service
from app.repositories.user_repository import UserRepository


def verify_user(custom_session_id: str = Cookie(None)):
    session_id = custom_session_id
    auth_service_object = auth_service.AuthService(UserRepository(SessionLocal))
    if session_id is None:
        status = False
        user_id=None
        session_id=None
    else:
        status, user_id = auth_service_object.check_auth(SessionSearchingParams(id=session_id))


    return {"status": status, "user_id": user_id, "session_id": session_id, "message": "you are not authorizate"}

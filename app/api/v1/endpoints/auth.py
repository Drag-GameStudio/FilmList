# regist, login, check login
from fastapi import APIRouter, Depends, Response
from app.schema.auth_schema import UserInfo, SessionSearchingParams
from app.db.database import get_db, SessionLocal

from app.services import auth_service
from app.repositories.user_repository import UserRepository
from app.core.dependencies import verify_user

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/regist")
def regist(user_info: UserInfo):
    auth_service_object = auth_service.AuthService(UserRepository(SessionLocal))
    status, created_object =  auth_service_object.regist(user_info)
    if status:
        return {"status": "success", "message": created_object}
    
    return {"status": "error", "message": "this username has already taken"}



@router.post("/login")
def login(response: Response, user_params: UserInfo):
    auth_service_object = auth_service.AuthService(UserRepository(SessionLocal))
    status, detail = auth_service_object.login(user_params)

    if status:
        response.set_cookie(
            key="custom_session_id",
            value=detail,
            max_age=3600 * 24 * 30,
            httponly=False,
        )
        return {"status": "success"}
    
    return {"status": "error", "message": detail}

@router.get("/check_auth")
def check_auth(verify_data = Depends(verify_user)):
    message = verify_data["message"]
    if verify_data["status"]:
        return {"status": "success"}
    return {"status": "error", "message": message}

@router.post("/logout")
def logout(verify_data = Depends(verify_user)):
    message = verify_data["message"]

    if verify_data["status"]:
        auth_service_object = auth_service.AuthService(UserRepository(SessionLocal))
        status = auth_service_object.logout(SessionSearchingParams(id=verify_data["session_id"]))

        if status == True:
            return {"status": "success"}
        
        message = "problem with logout"

    return {"status": "error", "message": message}
    





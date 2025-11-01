from fastapi import APIRouter
from .endpoints import auth, film, review


routers = APIRouter(prefix="/v1")
router_list = [auth.router, film.router, review.router]

for router in router_list:
    router.tags = router.tags.append("v1")
    routers.include_router(router)
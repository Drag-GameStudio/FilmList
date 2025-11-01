from fastapi import FastAPI
from app.api.v1.routes import routers as v1_api_router
from app.db.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware




app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # твой фронтенд
    allow_credentials=True,                   # обязательно!
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(v1_api_router)

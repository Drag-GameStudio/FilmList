from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.util.hash import get_rand_hash
from app.util.hash import verify_password, hash_password


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(length=256), unique=True, index=True)
    _password = Column(String(length=300))

    wish_list = relationship("WishList", uselist=False, back_populates="user", cascade="all, delete-orphan")

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value: str):
        self._password = hash_password(value)

    def check_password(self, password: str) -> bool:
        return verify_password(password, self._password)
    
    



class Session(Base):
    __tablename__ = "session"

    id = Column(String(length=32), primary_key=True, index=True, default=get_rand_hash)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")   

    def __repr__(self):
        return self.id
    



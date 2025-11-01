from sqlalchemy import Table, Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base

wish_list_films = Table(
    "wish_list_films",
    Base.metadata,
    Column("wish_list_id", ForeignKey("wish_list.user_id"), primary_key=True),
    Column("film_id", ForeignKey("films.id"), primary_key=True),
)


class Film(Base):
    __tablename__ = "films"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    image = Column(String)


class WishList(Base):
    __tablename__ = "wish_list"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    user = relationship("User", back_populates="wish_list")
    films = relationship("Film", secondary=wish_list_films)

    def get_films(self):
        return list(map(lambda obj: obj.id, list(self.films)))


class FilmReview(Base):
    __tablename__ = "films_reviews"

    review_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")

    film_id = Column(Integer, ForeignKey("films.id"))
    film = relationship("Film")

    content = Column(String)

    rate = Column(Integer)

    __table_args__ = (
        UniqueConstraint('user_id', 'film_id', name='uq_user_film_review'),
    )
import os

from fastapi import status
from sqlmodel import SQLModel, create_engine, Session, select
from fastapi import Depends, HTTPException

from models.film import Film


sqlite_url = os.environ["DATABASE_URL"]

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


class Session(Session):
    def first_or_none(self, entity, *criterion):
        return self.exec(
            select(entity).where(*criterion)
        ).first()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


async def get_film_from_database(
    film_id: int,
    session: Session = Depends(get_session),
) -> Film:
    film = session.get(Film, film_id)

    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Film not found"
        )

    return film

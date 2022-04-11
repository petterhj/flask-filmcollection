import os

from fastapi import status
from sqlmodel import SQLModel, create_engine, Session, select
from fastapi import Depends, HTTPException

from models.film import Film
from models.genre import Genre
from models.media import Media


sqlite_url = os.environ["DATABASE_URL"]

engine = create_engine(
    sqlite_url,
    echo=True,
    connect_args={
        "check_same_thread": False,
    },
)


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
    slug: str,
    session: Session = Depends(get_session),
) -> Film:
    if film := session.first_or_none(Film, Film.lb_slug == slug):
        return film

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Film not found"
    )


async def get_genre_from_database(
    slug: str,
    session: Session = Depends(get_session),
) -> Genre:
    if genre := session.first_or_none(Genre, Genre.slug == slug):
        return genre

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Genre not found"
    )


async def get_media_from_database(
    barcode: int,
    session: Session = Depends(get_session),
) -> Media:
    if media := session.first_or_none(Media, Media.barcode == barcode):
        return media

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Media not found"
    )
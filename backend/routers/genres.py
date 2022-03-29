from typing import List

from fastapi import (
    APIRouter,
    Depends,
)
from sqlmodel import Session, select

from database import get_session, get_genre_from_database
from models.film import Film, FilmRead
from models.genre import Genre, GenreRead, GenreReadDetails


router = APIRouter(prefix="/genres")


@router.get(
    "/",
    response_model=List[GenreRead],
)
async def get_genres(session: Session = Depends(get_session)):
    return session.exec(select(Genre)).all()


@router.get(
    "/{slug}",
    response_model=GenreReadDetails,
)
async def get_genres(genre: Genre = Depends(get_genre_from_database)):
    return genre

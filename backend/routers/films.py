import os
import shutil
import requests
from datetime import datetime
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import RedirectResponse, FileResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from database import get_session, get_film_from_database
from models.country import Country
from models.film import (
    Film,
    FilmPatch,
    FilmRead,
    FilmReadDetails,
)
from models.genre import Genre
from models.language import Language
from models.people import Person


router = APIRouter(prefix="/films")


@router.get(
    "/",
    response_model=List[FilmRead],
    response_model_by_alias=False,
)
async def get_films(session: Session = Depends(get_session)):
    return session.exec(select(Film)).all()


@router.get(
    "/import",
    response_class=RedirectResponse,
    status_code=status.HTTP_302_FOUND,
)
async def add_films(
    imdb_id: str = Query(..., regex="^tt\d{7,8}$"),
    session: Session = Depends(get_session),
    # token: str = Depends(oauth2_scheme)
):
    if existing_film := session.first_or_none(Film, Film.imdb_id == imdb_id):
        return router.url_path_for("get_film", film_id=existing_film.id)

    r = requests.get("http://www.omdbapi.com", params={
        "apikey": os.environ["OMDB_API_KEY"],
        "i": imdb_id,
    }).json()

    if r["Response"] == "False":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=r["Error"],
        )

    genres = []
    for genre_name in [g.strip() for g in r["Genre"].split(",")]:
        existing = session.first_or_none(Genre, Genre.name == genre_name)
        genres.append(existing or Genre(name=genre_name))

    directors = []
    for person_name in [p.strip() for p in r["Director"].split(",")]:
        existing = session.first_or_none(Person, Person.name == person_name)
        directors.append(existing or Person(name=person_name))

    writers = []
    for person_name in [p.strip() for p in r["Writer"].split(",")]:
        existing = session.first_or_none(Person, Person.name == person_name)
        to_be_added_director = None
        for director in directors:
            if director.name == person_name:
                to_be_added_director = director
        writers.append(existing or to_be_added_director or Person(name=person_name))

    countries = []
    for country in [c.strip() for c in r["Country"].split(",")]:
        existing = session.first_or_none(Country, Country.name == country)
        countries.append(existing or Country(name=country))

    languages = []
    for language in [l.strip() for l in r["Language"].split(",")]:
        existing = session.first_or_none(Language, Language.name == language)
        languages.append(existing or Language(name=language))

    film = Film.parse_obj({**r, **{
        "imdb_id": imdb_id,
        "genres": genres,
        "directors": directors,
        "writers": writers,
        "countries": countries,
        "languages": languages,
    }})

    try:
        session.add(film)
        session.commit()
        session.refresh(film)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Database integrity error",
        )

    poster_path = os.path.join(
        os.environ["MEDIA_ROOT"], "posters", f"{film.id}-poster.jpg"
    )

    if not os.path.exists(os.path.dirname(poster_path)):
        os.makedirs(os.path.dirname(poster_path))

    if r["Poster"] and not os.path.isfile(poster_path):
        r = requests.get(r["Poster"], stream=True)
        if r.status_code == 200:
            with open(poster_path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

    return router.url_path_for("get_film", film_id=film.id)


@router.get(
    "/{film_id}",
    response_model=FilmReadDetails,
    response_model_by_alias=False,
)
async def get_film(
    film: Film = Depends(get_film_from_database)
):
    return film


@router.patch(
    "/{film_id}",
    response_model=FilmRead,
    response_model_by_alias=False,
)
async def get_film(
    patch: FilmPatch,
    film: Film = Depends(get_film_from_database),
    session: Session = Depends(get_session),
):
    patch = patch.dict(exclude_unset=True)

    if not patch:
        return film

    for key, value in patch.items():
        setattr(film, key, value)

    session.add(film)
    session.commit()
    session.refresh(film)

    return film


@router.delete(
    "/{film_id}",
    status_code=status.HTTP_200_OK,
)
async def get_film(
    film: Film = Depends(get_film_from_database),
    session: Session = Depends(get_session),
):
    session.delete(film)
    session.commit()
    return {"message": "OK"}


@router.get(
    "/{film_id}/poster.jpg",
    response_class=FileResponse,
)
async def get_film_poster(
    film: Film = Depends(get_film_from_database)
):
    poster_path = os.path.join(
        os.environ["MEDIA_ROOT"], "posters", f"{film.id}-poster.jpg"
    )

    if not os.path.isfile(poster_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No poster found"
        )

    return FileResponse(poster_path)

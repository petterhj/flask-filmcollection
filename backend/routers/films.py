import os
import shutil
from datetime import datetime
from typing import List

import requests
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import FileResponse
from requests.exceptions import ConnectionError
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
from models.services import OmdbSearchResult


router = APIRouter(prefix="/films")


@router.get(
    "/",
    response_model=List[FilmRead],
)
async def get_films(session: Session = Depends(get_session)):
    return session.exec(select(Film)).all()


@router.get(
    "/{slug}",
    response_model=FilmReadDetails,
)
async def get_film(
    film: Film = Depends(get_film_from_database)
):
    return film


@router.patch(
    "/{slug}",
    response_model=FilmReadDetails,
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
    "/{slug}",
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
    "/{slug}/poster.jpg",
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


@router.get(
    "/{slug}/search",
    response_model=List[OmdbSearchResult],
    response_model_by_alias=False,
)
async def add_films(
    film: Film = Depends(get_film_from_database),
    session: Session = Depends(get_session),
    # token: str = Depends(oauth2_scheme)
):
    results = []

    for title in (film.title, film.display_title):
        if not title:
            continue

        r = requests.get("http://www.omdbapi.com", params={
            "apikey": os.environ["OMDB_API_KEY"],
            "s": title,
            "y": film.year,
        }).json()

        if r["Response"] == "False":
            if r["Error"] == "Movie not found!":
                continue
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=r["Error"],
            )
        
        results = [OmdbSearchResult(**film) for film in r["Search"]]
    
    return results


@router.get(
    "/{slug}/refresh",
    response_model=FilmReadDetails,
)
async def add_films(
    film: Film = Depends(get_film_from_database),
    imdb_id: str = Query(..., regex="^tt\d{7,8}$"),
    session: Session = Depends(get_session),
    # token: str = Depends(oauth2_scheme)
):
    try:
        r = requests.get("http://www.omdbapi.com", params={
            "apikey": os.environ["OMDB_API_KEY"],
            "i": imdb_id,
        }).json()
    except ConnectionError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not connect to OMDB API",
        )

    if r["Response"] == "False":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=r["Error"],
        )

    film_patch = FilmPatch.parse_obj({**r, **{"imdb_id": imdb_id}})

    for key, value in film_patch.dict(exclude_defaults=True).items():
        setattr(film, key, value)

    for genre_name in [g.strip() for g in r["Genre"].split(",")]:
        existing = session.first_or_none(Genre, Genre.name == genre_name)
        genre = existing or Genre(name=genre_name)
        if genre not in film.genres:
            film.genres.append(genre)

    for person_name in [p.strip() for p in r["Director"].split(",")]:
        existing = session.first_or_none(Person, Person.name == person_name)
        director = existing or Person(name=person_name)
        if director not in film.directors:
            film.directors.append(director)

    for person_name in [p.strip() for p in r["Writer"].split(",")]:
        existing = session.first_or_none(Person, Person.name == person_name)
        to_be_added_director = None
        for director in film.directors:
            if director.name == person_name:
                to_be_added_director = director
        writer = existing or to_be_added_director or Person(name=person_name)
        if writer not in film.writers:
            film.writers.append(writer)

    for country in [c.strip() for c in r["Country"].split(",")]:
        existing = session.first_or_none(Country, Country.name == country)
        country = existing or Country(name=country)
        if country not in film.countries:
            film.countries.append(country)

    for language in [l.strip() for l in r["Language"].split(",")]:
        existing = session.first_or_none(Language, Language.name == language)
        language = existing or Language(name=language)
        if language not in film.languages:
            film.languages.append(language)

    session.add(film)
    session.commit()
    session.refresh(film)


    poster_path = os.path.join(
        os.environ["MEDIA_ROOT"], "posters", f"{film.id}-poster.jpg"
    )

    if not os.path.exists(os.path.dirname(poster_path)):
        os.makedirs(os.path.dirname(poster_path))

    if r["Poster"]:
        r = requests.get(r["Poster"], stream=True)
        if r.status_code == 200:
            with open(poster_path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

    return film

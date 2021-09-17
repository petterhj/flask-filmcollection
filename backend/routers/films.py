import os
import shutil
import requests
from datetime import datetime   
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database import get_session
from models import Film


router = APIRouter(prefix="/films")


@router.get("/", response_model=List[Film])
async def get_films(session: Session = Depends(get_session)):
    films = session.exec(select(Film)).all()
    return films



"""
async def get_film(film_id: int) -> Film:
    film = await Film.get_or_none(id=film_id)
    
    if not film:
        raise HTTPException(status_code=404, detail=f"Film {film_id} not found")

    return film


async def get_release(release_id: int, film: Film = Depends(get_film)) -> Release:
    release = await Release.get_or_none(film=film, id=release_id)
    
    if not release:
        raise HTTPException(
            status_code=404,
            detail=f"Release {release_id} for film {film.id} not found"
        )
    
    return release


@router.get("/", response_model=List[FilmWithReleasesSchema])
async def get_films():
    qs = Film.all().order_by("title")
    return await FilmWithReleasesSchema.from_queryset(qs)


@router.post("/import", response_model=FilmSchema)
# async def add_films(query: FilmInSchema, token: str = Depends(oauth2_scheme)):
async def add_films(query: FilmInSchema):
    r = requests.get("http://www.omdbapi.com", params={
        "apikey": os.environ.get("OMDB_API_KEY"),
        "i": query.imdb_id,
    }).json()

    if r["Response"] == "False":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=r["Error"])

    metadata = {
        "title": r["Title"],
        "genre": r["Genre"],
        "director": r["Director"],
        "country": r["Country"],
        "language": r["Language"],
        "summary": r["Plot"],
        "runtime": int(r["Runtime"].replace("min", "").strip()),
        "release_date": datetime.strptime(r["Released"], "%d %b %Y"),
    }

    film, created = await Film.update_or_create(
        imdb_id=r["imdbID"],
        defaults=metadata,
    )

    poster_path = os.path.join(
        os.environ["MEDIA_ROOT"], f"{film.id}-poster.jpg"
    )

    if r["Poster"] and not os.path.isfile(poster_path):
        r = requests.get(r["Poster"], stream=True)
        if r.status_code == 200:
            with open(poster_path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

    return film


@router.delete("/{film_id}", status_code=status.HTTP_200_OK)
async def delete_film(film: Film = Depends(get_film)):
    await film.delete()
    return {"message": "OK"}


@router.post(
    "/{film_id}/releases",
    status_code=status.HTTP_201_CREATED,
    response_model=ReleaseSchema,
)
async def add_release(
    release_in: ReleaseInSchema,
    film: Film = Depends(get_film)
):
    return await Release.create(
        film=film,
        **release_in.dict(exclude_unset=True)
    )

@router.delete(
    "/{film_id}/releases/{release_id}",
    status_code=status.HTTP_200_OK,
    responses={404: {"model": HTTPNotFoundError}}
)
async def delete_release(release: Release = Depends(get_release)):
    await release.delete()
    return {"message": "OK"}
"""
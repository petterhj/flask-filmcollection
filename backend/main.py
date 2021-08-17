from typing import List

from fastapi import FastAPI, Depends, Response, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from tortoise.contrib.fastapi import HTTPNotFoundError

from db import init_db
from models import (
    Film, FilmSchema,
    Release, ReleaseSchema, ReleaseInSchema,
    FilmWithReleasesSchema, 
)
from tortoise.query_utils import Prefetch


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    init_db(app)


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


@app.get("/", response_model=List[FilmWithReleasesSchema])
async def get_films():
    qs = Film.all().order_by("title")
    films = await FilmWithReleasesSchema.from_queryset(qs)
    for film in films:
        print(film.json())
    return films


@app.delete("/{film_id}", status_code=status.HTTP_200_OK)
async def delete_film(film: Film = Depends(get_film)):
    await film.delete()
    return {"message": "OK"}


@app.post(
    "/{film_id}/releases",
    status_code=status.HTTP_201_CREATED,
    response_model=ReleaseSchema,
)
async def add_release(release_in: ReleaseInSchema, film: Film = Depends(get_film)):
    return await Release.create(
        film=film,
        **release_in.dict(exclude_unset=True)
    )

@app.delete(
    "/{film_id}/releases/{release_id}",
    status_code=status.HTTP_200_OK,
    responses={404: {"model": HTTPNotFoundError}}
)
async def delete_release(release: Release = Depends(get_release)):
    await release.delete()
    return {"message": "OK"}

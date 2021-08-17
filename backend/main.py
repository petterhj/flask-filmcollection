from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tortoise.contrib.starlette import register_tortoise

from db import init_db
from models import Film, FilmSchema, Release, FilmWithReleasesSchema
from tortoise.query_utils import Prefetch


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    init_db(app)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/films", response_model=List[FilmWithReleasesSchema])
async def get_films():
    qs = Film.all()#.prefetch_related("releases")
    films = await FilmWithReleasesSchema.from_queryset(qs)
    for film in films:
        print(film.json())
    return films

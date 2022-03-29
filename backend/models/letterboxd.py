from typing import List

from pydantic import BaseModel

from models.media import MediaType


class LetterboxdFilm(BaseModel):
    slug: str
    title: str
    year: int


class LetterboxdList(BaseModel):
    slug: str
    title: str = None
    media_type: MediaType
    films: List[LetterboxdFilm] = []

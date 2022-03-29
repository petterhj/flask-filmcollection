from enum import Enum
from typing import List

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    validator
)

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


class OmdbProductionType(str, Enum):
    MOVIE = "movie"
    SERIES = "series"
    EPISODE = "episode"


class OmdbSearchResult(BaseModel):
    imdb_id: str = Field(..., regex="^tt\d{7,8}$", alias="imdbID")
    title: str = Field(..., alias="Title")
    year: int = Field(None, alias="Year")
    production_type: OmdbProductionType = Field(..., alias="Type")
    poster_url: HttpUrl = Field(None, alias="Poster")

    @validator("poster_url", pre=True)
    def validate_poster_url(cls, v):
        return v if v != "N/A" else None

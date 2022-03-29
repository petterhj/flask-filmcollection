import os
from enum import Enum
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime, date
from pydantic import validator

from pydantic import BaseModel
from sqlalchemy import String
from sqlalchemy.sql.schema import Column
from sqlmodel import (
    Field, SQLModel, Relationship
)

from .country import Country, CountryRead
from .genre import Genre, GenreRead
from .language import Language, LanguageRead
from .links import (
    FilmGenreLink, FilmDirectorLink, FilmWriterLink,
    FilmCountryLink, FilmLanguageLink
)
from .media import CollectedMedia, CollectedMediaRead
from .people import Person, PersonRead



class ExportPropertiesMixin(BaseModel):
    @classmethod
    def get_properties(cls):
        return [prop for prop in dir(cls) if isinstance(
            getattr(cls, prop
        ), property) and prop not in ("__values__", "fields")]

    def dict(self, *args, **kwargs):
        attribs = super().dict(*args, **kwargs)
        props = self.get_properties()
        if props:
            attribs.update({
                prop: getattr(self, prop) for prop in props
            })
        return attribs


class ProductionType(str, Enum):
    MOVIE = "movie"
    SERIES = "series"


class FilmBase(SQLModel):
    title: str = Field(
        min_length=1,
        max_length=125,
    )
    display_title: str = Field(None,
        min_length=1,
        max_length=125,
    )
    year: int
    lb_slug: str = Field(
        None,
        sa_column=Column("lb_slug", String, unique=True),
        regex="^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    imdb_id: str = Field(
        None,
        sa_column=Column("imdb_id", String, unique=True),
        regex="^tt\d{7,8}$",
    )
    tmdb_id: str = Field(
        None,
        sa_column=Column("tmdb_id", String, unique=True),
        regex="[0-9]+",
    )
    release_date: date = None
    production_type: ProductionType = Field(ProductionType.MOVIE)

    class Config:
        allow_population_by_field_name = True
        by_alias = False
        validate_assignment = True


class Film(FilmBase, table=True):
    id: Optional[int] = Field(None, primary_key=True)
    summary: str
    runtime: int
    meta_score: int
    imdb_rating: float

    genres: List[Genre] = Relationship(
        link_model=FilmGenreLink,
        back_populates="films",
    )
    directors: List[Person] = Relationship(
        link_model=FilmDirectorLink,
        back_populates="directed",
    )
    writers: List[Person] = Relationship(
        link_model=FilmWriterLink,
        back_populates="written",
    )
    countries: List[Country] = Relationship(
        link_model=FilmCountryLink,
        back_populates="films",
    )
    languages: List[Language] = Relationship(
        link_model=FilmLanguageLink,
        back_populates="films",
    )
    media: List[CollectedMedia] = Relationship(
        back_populates="film",
    )


class FilmRead(FilmBase, ExportPropertiesMixin):
    id: int
    media: List[CollectedMediaRead] = []

    @property
    def has_poster(self):
        return os.path.exists(os.path.join(
            os.environ["MEDIA_ROOT"], "posters", f"{self.id}-poster.jpg"
        ))


class FilmReadDetails(FilmRead):
    summary: Optional[str]
    runtime: Optional[int]
    meta_score: Optional[int]
    imdb_rating: Optional[float]

    genres: List[GenreRead] = []
    directors: List[PersonRead] = []
    writers: List[PersonRead] = []
    countries: List[CountryRead] = []
    languages: List[LanguageRead] = []

    @property
    def has_poster(self):
        return os.path.exists(os.path.join(
            os.environ["MEDIA_ROOT"], "posters", f"{self.id}-poster.jpg"
        ))


class FilmPatch(FilmBase):
    title: Optional[str] = Field(alias="Title")
    display_title: Optional[str]
    year: Optional[int] = Field(alias="Year")
    release_date: Optional[date] = Field(alias="Released")
    summary: Optional[str] = Field(alias="Plot")
    runtime: Optional[int] = Field(alias="Runtime")
    imdb_id: Optional[str]
    tmdb_id: Optional[str]
    lb_slug: Optional[str]
    meta_score: Optional[int] = Field(alias="Metascore")
    imdb_rating: Optional[float] = Field(alias="imdbRating")
    production_type: ProductionType = Field(alias="Type")

    genres: Optional[List[Genre]] = []
    directors: Optional[List[Person]] = []
    writers: Optional[List[Person]] = []
    countries: Optional[List[Country]] = []
    languages: Optional[List[Language]] = []

    @validator("release_date", pre=True)
    def validate_release_date(cls, v):
        try:
            return datetime.strptime(v, "%d %b %Y")
        except TypeError:
            return v

    @validator("year", pre=True)
    def validate_year(cls, v):
        if isinstance(v, str):
            return v[0:4] # Make sure only first year (if tv show) is used
        return v

    @validator("runtime", pre=True)
    def validate_runtime(cls, v):
        if isinstance(v, str) and v != "N/A":
            return int(v.replace("min", "").strip())
        return v

    class Config:
        extra = "ignore"

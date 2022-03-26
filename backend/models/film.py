import os
from enum import Enum
from typing import List, Optional
from datetime import date
from pydantic import validator

from pydantic import BaseModel
from sqlalchemy import String
from sqlalchemy.sql.schema import Column
from sqlmodel import (
    Field, SQLModel, Relationship
)

from .genre import Genre, GenreRead
from .people import Person, PersonRead
from .language import Language, LanguageRead
from .country import Country, CountryRead
from .links import (
    FilmGenreLink, FilmDirectorLink, FilmWriterLink,
    FilmCountryLink, FilmLanguageLink
)


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
    title: str = Field(...,
        alias="Title",
        min_length=1,
        max_length=125,
    )
    display_title: Optional[str] = Field(None,
        min_length=1,
        max_length=125,
    )
    year: int = Field(..., alias="Year")
    imdb_id: str = Field(
        sa_column=Column("imdb_id", String, unique=True),
        regex="^tt\d{7,8}$",
    )
    tmdb_id: Optional[str] = Field(
        sa_column=Column("tmdb_id", String, unique=True),
        regex="[0-9]+",
    )
    lb_slug: Optional[str] = Field(
        sa_column=Column("lb_slug", String, unique=True),
        regex="^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    release_date: Optional[date] = Field(None, alias="Released")
    summary: Optional[str] = Field(None, alias="Plot")
    runtime: Optional[int] = Field(None, alias="Runtime")
    meta_score: Optional[int] = Field(None, alias="Metascore")
    imdb_rating: Optional[float] = Field(None, alias="imdbRating")
    production_type: ProductionType = Field(..., alias="Type")

    class Config:
        allow_population_by_field_name = True
        by_alias = False
        validate_assignment = True


class Film(FilmBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

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

    @validator("year", pre=True)
    def validate_year(cls, v):
        if isinstance(v, str):
            return v[0:4] # Make sure only first year (if tv show) is used
        return v

    @validator("runtime", pre=True)
    def validate_runtime(cls, v):
        if isinstance(v, str):
            return v.replace("min", "").strip()


class FilmRead(FilmBase, ExportPropertiesMixin):
    id: int

    @property
    def has_poster(self):
        return os.path.exists(os.path.join(
            os.environ["MEDIA_ROOT"], "posters", f"{self.id}-poster.jpg"
        ))


class FilmReadDetails(FilmRead):
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


class FilmPatch(BaseModel):
    title: Optional[str]
    display_title: Optional[str]
    year: Optional[int]
    release_date: Optional[date]
    summary: Optional[str]
    runtime: Optional[int]
    imdb_id: Optional[str]
    tmdb_id: Optional[str]
    lb_slug: Optional[str]
    meta_score: Optional[int]
    imdb_rating: Optional[float]

    class Config:
        extra = "forbid"
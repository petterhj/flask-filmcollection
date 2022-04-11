from typing import Optional

from sqlmodel import Field, SQLModel


class FilmGenreLink(SQLModel, table=True):
    film_id: Optional[int] = Field(
        default=None, foreign_key="film.id", primary_key=True
    )
    genre_id: Optional[int] = Field(
        default=None, foreign_key="genre.id", primary_key=True
    )


class FilmDirectorLink(SQLModel, table=True):
    film_id: Optional[int] = Field(
        default=None, foreign_key="film.id", primary_key=True
    )
    person_id: Optional[int] = Field(
        default=None, foreign_key="person.id", primary_key=True
    )


class FilmWriterLink(SQLModel, table=True):
    film_id: Optional[int] = Field(
        default=None, foreign_key="film.id", primary_key=True
    )
    person_id: Optional[int] = Field(
        default=None, foreign_key="person.id", primary_key=True
    )


class FilmCountryLink(SQLModel, table=True):
    film_id: Optional[int] = Field(
        default=None, foreign_key="film.id", primary_key=True
    )
    country_id: Optional[int] = Field(
        default=None, foreign_key="country.id", primary_key=True
    )


class FilmLanguageLink(SQLModel, table=True):
    film_id: Optional[int] = Field(
        default=None, foreign_key="film.id", primary_key=True
    )
    language_id: Optional[int] = Field(
        default=None, foreign_key="language.id", primary_key=True
    )


class FilmMediaLink(SQLModel, table=True):
    film_id: Optional[int] = Field(
        default=None, foreign_key="film.id", primary_key=True
    )
    media_id: Optional[int] = Field(
        default=None, foreign_key="media.id", primary_key=True
    )

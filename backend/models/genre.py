from typing import List, Optional

from sqlmodel import (
    Field, SQLModel, Relationship
)

from .links import FilmGenreLink


class GenreBase(SQLModel):
    name: str


class Genre(GenreBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    films: List["Film"] = Relationship(
        link_model=FilmGenreLink,
        back_populates="genres",
    )


class GenreRead(GenreBase):
    id: int

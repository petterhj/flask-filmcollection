from typing import TYPE_CHECKING, List, Optional

from pydantic import root_validator
from slugify import slugify
from sqlmodel import (
    Field, SQLModel, Relationship
)

from .links import FilmGenreLink

# if TYPE_CHECKING:
#     from models.film import Film


class GenreBase(SQLModel):
    name: str
    slug: str

    @root_validator
    def create_slug(cls, values):
        values["slug"] = slugify(values["name"])
        return values


class Genre(GenreBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    films: List["Film"] = Relationship(
        link_model=FilmGenreLink,
        back_populates="genres",
    )


class GenreRead(GenreBase):
    pass


class GenreReadDetails(GenreRead):
    # from models.film import Film

    # films: List["Film"]
    # films: List["FilmRead"] = []
    pass

# from models.film import FilmRead
# GenreReadDetails.update_forward_refs()

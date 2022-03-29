from typing import List, Optional

from pydantic import root_validator
from slugify import slugify
from sqlmodel import (
    Field, SQLModel, Relationship
)

from .links import FilmCountryLink


class CountryBase(SQLModel):
    name: str
    slug: str

    @root_validator
    def create_slug(cls, values):
        values["slug"] = slugify(values["name"])
        return values


class Country(CountryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    films: List["Film"] = Relationship(
        link_model=FilmCountryLink,
        back_populates="countries",
    )


class CountryRead(CountryBase):
    id: int

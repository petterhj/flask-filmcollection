from typing import List, Optional

from pydantic import root_validator
from slugify import slugify
from sqlmodel import (
    Field, SQLModel, Relationship
)

from .links import FilmDirectorLink, FilmWriterLink


class PersonBase(SQLModel):
    name: str
    slug: str

    @root_validator
    def create_slug(cls, values):
        values["slug"] = slugify(values["name"])
        return values


class Person(PersonBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    directed: List["Film"] = Relationship(
        link_model=FilmDirectorLink,
        back_populates="directors",
    )

    written: List["Film"] = Relationship(
        link_model=FilmWriterLink,
        back_populates="writers",
    )


class PersonRead(PersonBase):
    pass

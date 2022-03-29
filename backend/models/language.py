from typing import List, Optional

from pydantic import root_validator
from slugify import slugify
from sqlmodel import (
    Field, SQLModel, Relationship
)

from .links import FilmLanguageLink


class LanguageBase(SQLModel):
    name: str
    slug: str

    @root_validator
    def create_slug(cls, values):
        values["slug"] = slugify(values["name"])
        return values


class Language(LanguageBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    films: List["Film"] = Relationship(
        link_model=FilmLanguageLink,
        back_populates="languages",
    )


class LanguageRead(LanguageBase):
    pass

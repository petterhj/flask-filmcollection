from typing import List, Optional

from sqlmodel import (
    Field, SQLModel, Relationship
)

from .links import FilmLanguageLink


class LanguageBase(SQLModel):
    name: str


class Language(LanguageBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    films: List["Film"] = Relationship(
        link_model=FilmLanguageLink,
        back_populates="languages",
    )


class LanguageRead(LanguageBase):
    id: int

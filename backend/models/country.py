from typing import List, Optional

from sqlmodel import (
    Field, SQLModel, Relationship
)

from .links import FilmCountryLink


class CountryBase(SQLModel):
    name: str


class Country(CountryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    films: List["Film"] = Relationship(
        link_model=FilmCountryLink,
        back_populates="countries",
    )


class CountryRead(CountryBase):
    id: int

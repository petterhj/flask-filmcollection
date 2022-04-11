from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Integer
from sqlalchemy.sql.schema import Column
from sqlmodel import Field, Relationship, SQLModel

from .links import FilmMediaLink


class MediaType(str, Enum):
    DVD = "dvd"
    BR = "br"
    UHD = "uhd"


class MediaBase(SQLModel):
    media_type: MediaType
    barcode: Optional[int] = Field(
        sa_column=Column("barcode", Integer, unique=True),
    )


class Media(MediaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    films: List["Film"] = Relationship(
        link_model=FilmMediaLink,
        back_populates="media",
    )


class MediaCreate(MediaBase):
    pass


class MediaRead(MediaBase):
    id: int


class MediaReadDetails(MediaRead):
    films: List["FilmRead"] = []

from .film import FilmRead
MediaReadDetails.update_forward_refs()

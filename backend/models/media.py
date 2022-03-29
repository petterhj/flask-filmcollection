from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Integer
from sqlalchemy.sql.schema import Column
from sqlmodel import Field, Relationship, SQLModel


class MediaType(str, Enum):
    DVD = "dvd"
    BR = "br"
    UHD = "uhd"


class CollectedMediaBase(SQLModel):
    media_type: MediaType
    barcode: Optional[int] = Field(
        sa_column=Column("barcode", Integer, unique=True),
    )
    added_at: datetime = Field(
        default_factory=datetime.now,
    )


class CollectedMedia(CollectedMediaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    film_id: int = Field(
        foreign_key="film.id",
    )
    film: "Film" = Relationship(
        back_populates="media",
    )


class CollectedMediaRead(CollectedMediaBase):
    id: int

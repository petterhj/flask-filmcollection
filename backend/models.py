from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, constr
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Film(models.Model):
    title = fields.CharField(max_length=255)
    genre = fields.CharField(max_length=255, null=True)
    director = fields.CharField(max_length=255, null=True)
    country = fields.CharField(max_length=255, null=True)
    language = fields.CharField(max_length=255, null=True)
    summary = fields.TextField(null=True)
    runtime = fields.IntField(null=True)
    release_date = fields.DateField(null=True)

    # tmdb_id = fields.CharField(max_length=15, unique=True)
    imdb_id = fields.CharField(max_length=15, unique=True)#, null=True)

    releases: fields.ReverseRelation["Release"]

    # def collected_releases(self) -> int:
    #     # return len(self.releases)
    #     print(self.releases)
    #     print(len(self.releases))
    #     return 0

    # class PydanticMeta:
    #     computed = ["collected_releases"]


class ReleaseFormat(str, Enum):
    VHS = "VHS"
    DVD = "DVD"
    BD = "BD"
    UHD = "UHD"


class Release(models.Model):
    film = fields.ForeignKeyField(
        "models.Film",
        related_name="releases",
    )
    release_format = fields.CharEnumField(ReleaseFormat)
    barcode = fields.CharField(max_length=25, null=True)
    added_date = fields.DateField(null=True)


FilmSchema = pydantic_model_creator(Film, name="Film")
ReleaseSchema = pydantic_model_creator(Release, name="Release")
# ReleaseInSchema = pydantic_model_creator(
#     Release,
#     name="ReleaseIn",
#     exclude_readonly=True,
#     exclude={"added_date",}
# )


class FilmWithReleasesSchema(FilmSchema):
    releases: List[ReleaseSchema]


class FilmInSchema(BaseModel):
    imdb_id: constr(regex=r"^tt[0-9]{7}$")


class ReleaseInSchema(BaseModel):
    release_format: ReleaseFormat
    barcode: Optional[constr(max_length=25)] = None


# print(FilmSchema.schema_json(indent=4))
# print(ReleaseSchema.schema_json(indent=4))
# print("--" * 10)
# print(ReleaseInSchema.schema_json(indent=4))

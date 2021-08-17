import os
from datetime import datetime

from tortoise import Tortoise, run_async

from models import Film, ReleaseFormat, Release


films = [
    {
        "title": "Budbringeren",
        "summary": "Foo bar",
        "release_date": "1996-01-01",
        "tmdb_id": "12345"
    },
    {
        "title": "Jernanger",
        "summary": None,
        "release_date": "2006-01-01",
        "tmdb_id": "23456"
    }
]


async def populate():
    await Tortoise.init(
        db_url=os.environ.get("DATABASE_URL"),
        modules={"models": ["models"]},
    )

    for film in films:
        f, created = await Film.get_or_create(**film)
        print(f.title, created)

        r, created = await Release.get_or_create(
            film=f,
            release_format=ReleaseFormat.DVD,
            barcode="abc123",
            added_date=datetime.now(),
        )
        print(r.release_format, created)


if __name__ == "__main__":
    run_async(populate())
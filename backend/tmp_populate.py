from datetime import datetime
from models import Film, ReleaseFormat, Release
from tortoise import Tortoise, run_async


async def populate():
    await Tortoise.init(
        db_url="sqlite://../data/db.sqlite",
        modules={"models": ["models"]},
    )

    film = await Film.get_or_create(
        title="Budbringeren",
        summary="Foo bar",
        release_date="1996-01-01",
        tmdb_id="12345",
    )
    print(film)
    # await film.save()
    # r1 = {}
    # r1 = await Release.create(
    #     film=film,
    #     release_format=ReleaseFormat.DVD,
    #     barcode="abc123",
    #     added_date=datetime.now(),
    # )
    # film.releases.add()


if __name__ == "__main__":
    run_async(populate())
import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy.orm import load_only
from sqlalchemy.sql.expression import func
from sqlmodel import select

load_dotenv()

from database import engine, Session
from models.film import Film
from models.services import LetterboxdList, LetterboxdFilm
from models.media import Media, MediaType

LETTERBOXD_LIST_URL = "https://letterboxd.com/{}/list/{}/detail/page/{}"
LETTERBOXD_USERNAME = os.environ["LB_USERNAME"]


def _parse_film_data(film_data) -> LetterboxdFilm:
    film_details = film_data.find("div", class_="film-detail-content")
    title = film_details.find("a")
    slug = title["href"].replace("/film/", "").replace("/", "").strip()
    title = title.get_text().strip()
    year = film_details.find("small").get_text().strip()
    return LetterboxdFilm(
        slug=slug,
        title=title,
        year=year,
    )


def scrape_letterboxd_list(letterboxd_list: LetterboxdList) -> LetterboxdList:
    next_page = 1

    while next_page:
        logger.info(f"Scraping list {list_slug}, page {next_page}")

        list_page = requests.get(LETTERBOXD_LIST_URL.format(
            LETTERBOXD_USERNAME, list_slug, next_page
        ))

        list_page.raise_for_status()

        soup = BeautifulSoup(list_page.content, "html.parser")

        if next_page == 1:
            list_title = soup.find("div", class_="list-title-intro").find("h1").get_text().strip()
            letterboxd_list.title = list_title

        film_list = soup.find("ul", class_="film-list").findAll("li")

        logger.debug(f"Found {len(film_list)} film(s)")

        for i, film in enumerate(film_list):
            letterboxd_list.films.append(_parse_film_data(film))
            # TODO: Temporary test, remove this
            if i == 2: break
        # TODO: Remove this
        break

        next_button = soup.find('a', class_='next')
        next_page = (next_page + 1) if next_button else None

    logger.info(f"Done scraping list")

    return letterboxd_list


def sync_letterboxd_list(
    list_slug: str,
    media_type: MediaType
):
    lb_list = scrape_letterboxd_list(LetterboxdList(
        slug=list_slug,
        media_type=media_type,
    ))

    session = Session(engine)

    lb_slugs = []

    for lb_film in lb_list.films:
        if film := session.first_or_none(Film, Film.lb_slug == lb_film.slug):
            logger.debug(f'Skipped adding film "{film.lb_slug}" from "{list_slug}"; already in database')

            existing_media_of_type = [
                m for m in film.media if m.media_type == lb_list.media_type
            ]

            if len(existing_media_of_type) > 0:
                logger.debug(f'Skipped adding media for "{film.lb_slug}"; {lb_list.media_type} already in database')
            else:
                film.media.append(Media(media_type=lb_list.media_type))
                film.commit()
                logger.debug(f'Adding {lb_list.media_type} media for "{film.lb_slug}"')
        else:
            # Add new film to database
            film = Film(
                title=lb_film.title,
                year=lb_film.year,
                lb_slug=lb_film.slug,
                media=[
                    Media(media_type=lb_list.media_type)
                ]
            )
            session.add(film)
            session.commit()
            logger.debug(f'Added film "{film.lb_slug}" from "{list_slug}"')

        lb_slugs.append(film.lb_slug)

    # Remove collected media (of type, and film if no more media)
    collected_not_in_remote = [
        film.lb_slug for film in session.query(
            Film
        ).options(
            load_only("lb_slug")
        ).filter(
            Film.media.any(Media.media_type == media_type)
        ).all() if film.lb_slug not in lb_slugs
    ]

    for slug in collected_not_in_remote:
        film = session.first_or_none(Film, Film.lb_slug == slug)
        if media_to_remove := [
            m for m in film.media if m.media_type == lb_list.media_type
        ]:
            for media in media_to_remove:
                film.media.remove(media)
            logger.debug('Removed {} {} media for "{}"'.format(
                len(media_to_remove), lb_list.media_type, film.lb_slug
            ))
        if len(film.media) == 0:
            logger.debug(f'Removed film "{film.lb_slug}"; no more media')
            session.delete(film)
    
    session.commit()

    # Clean any media not linked to any film
    for media in session.query(Media).all():
        if len(media.films) == 0:
            session.delete(media)

    session.commit()


if __name__ == "__main__":
    lists = os.environ["LB_LISTS"].split(",")

    for lb_list in lists:
        media_type, list_slug = lb_list.split(":")

        try:
            sync_letterboxd_list(
                list_slug=list_slug,
                media_type=MediaType(media_type)
            )
        except ValueError as e:
            logger.error(f"Skipping list, error={e}")

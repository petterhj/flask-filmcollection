import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

from database import engine, Session
from models.film import Film
from models.services import LetterboxdList, LetterboxdFilm
from models.media import CollectedMedia, MediaType

LETTERBOXD_LIST_URL = "https://letterboxd.com/{}/list/{}/detail/page/{}"
LETTERBOXD_USERNAME = os.environ["LB_USERNAME"]


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

        for film in film_list:
            film_details = film.find("div", class_="film-detail-content")
            title = film_details.find("a")
            slug = title["href"].replace("/film/", "").replace("/", "").strip()
            title = title.get_text().strip()
            year = film_details.find("small").get_text().strip()
            letterboxd_list.films.append(LetterboxdFilm(
                slug=slug,
                title=title,
                year=year,
            ))
            break
        break

        next_button = soup.find('a', class_='next')
        next_page = (next_page + 1) if next_button else None

    logger.info(f"Done scraping list")

    return letterboxd_list


def sync_letterboxd_list(
    list_slug: str,
    media_type: MediaType
):
    letterboxd_list = LetterboxdList(
        slug=list_slug,
        media_type=media_type,
    )
    letterboxd_list = scrape_letterboxd_list(letterboxd_list)

    session = Session(engine)

    for lb_film in letterboxd_list.films:
        if film := session.first_or_none(Film, Film.lb_slug == lb_film.slug):
            logger.debug(f"Skipping film {lb_film.slug} (already in database)")
        else:
            film = Film(
                title=lb_film.title,
                year=lb_film.year,
                lb_slug=lb_film.slug,
            )
            session.add(film)
            session.commit()

        if media := session.first_or_none(
            CollectedMedia,
            CollectedMedia.film == film,
            CollectedMedia.media_type == letterboxd_list.media_type,
        ):
            logger.debug("Skipping existing media {} for {} (already in database)".format(
                media.media_type, film.lb_slug
            ))
        else:
            session.add(CollectedMedia(
                media_type=letterboxd_list.media_type,
                film=film,
            ))
            session.commit()

    # Delete


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

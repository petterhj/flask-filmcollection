# Imports
import tmdbsimple
from loguru import logger
from html.parser import HTMLParser


# Class: TMDb
class TMDb(object):
    # Init
    def __init__(self, api_key):
        tmdbsimple.API_KEY = api_key

        self.html_parser = HTMLParser()
        self.tmdb_search = tmdbsimple.Search()


    # Search
    def search(self, title):
        logger.info('Searching films, title=%s' % (title))

        try:
            title = self.html_parser.unescape(title)
            results = self.tmdb_search.movie(query=title)
            results = results.get('results')
        except:
            logger.exception('Could not search TMDb')
            return []
        else:
            return results


    # Metadata
    def metadata(self, tmdb_id):
        logger.info('Fetching metadata, id=%s' % (str(tmdb_id)))

        try:
            movie = tmdbsimple.Movies(tmdb_id).info()
        except:
            logger.exception('Could not fetch TMDb metadata')
            return {}
        else:
            return movie
# Imports
from loguru import logger
from requests import Session
from bs4 import BeautifulSoup as soup

from config import BS_HTML_PARSER



# Constants
BASE_URL = 'https://letterboxd.com'
LOGIN_URL = BASE_URL + '/user/login.do'
LIST_URL = BASE_URL + '/%s/list/%s/page/%d'


# Class: Letterboxd
class Letterboxd(object):
    # Init
    def __init__(self, username, password):
        logger.info('Initializing Letterboxd')

        # Session
        self.username = username
        self.password = password
        self.session = None
        self.token = None


    # Create session
    def create_session(self):
        logger.info('Creating session for %s' % (self.username))

        try:
            client = Session()
            client.get(BASE_URL)
            token = client.cookies['com.xk72.webparts.csrf']  
            params = {'__csrf': token}
            auth = {'username': self.username, 'password': self.password} #, 'remember': True}  
            headers = {'Referer': BASE_URL}
            result = client.post(LOGIN_URL, data=dict(params, **auth), headers=headers)
            result = result.json()['result']

            logger.info('Got result "%s"' % (result))

            if result != 'success':
                logger.error('Could not log in (error: %s)' % (result))
                return None
        
        except Exception as e:
            logger.exception('Could not create session (error: %s)' % (e))
            return None

        else:
            logger.info('Logged in, csrf token = %s' % (params.get('__csrf')))
            logger.info('Headers:')
            for key, value in client.headers.iteritems():
                logger.info('> %s: %s' % (key, value))

            return client, params


    # Request
    def request(self, path, data={}, headers={}):
        # Check session
        if not self.session or not self.token:
            self.session, self.token = self.create_session()

        # Request
        logger.info('Requesting path=%s' % (path))
        r = self.session.get(path, data=data, headers=headers)

        return r.text.encode('utf-8')


    # List
    def list(self, list_name):
        # Parse watchlist
        logger.info('Requesting list "%s"' % (list_name))

        watchlist = {}

        current_page = 1
        has_next_page = True
        
        while has_next_page:
            wlsoup = soup(self.request(LIST_URL % (
                self.username, list_name, current_page
            )), BS_HTML_PARSER)

            for film in wlsoup.find_all('li', class_='poster-container'):
                container = film.find('div', class_='film-poster')
                poster = container.find('img')

                film_id = container.get('data-film-id')
                slug = container.get('data-target-link').replace('/film/', '').replace('/', '')
                title = poster.get('alt')

                watchlist[slug] = {
                    'id': film_id, 
                    'title': title
                }

            has_next_page = wlsoup.find('a', class_='next')
            current_page += 1

        return watchlist
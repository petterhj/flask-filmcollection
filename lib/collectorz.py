#!/usr/bin/python
# -*- coding: utf-8 -*-

# Imports
from loguru import logger
from requests import Session
from dateutil.parser import parse
from html.parser import HTMLParser
from bs4 import BeautifulSoup as soup

from config import BS_HTML_PARSER, MEDIA_EAN_COUNTRIES


# Constants
BASE_URL = 'http://core.collectorz.com'
SEARCH_URL = BASE_URL + '/movies/search?q=%s'
FILM_URL = BASE_URL + '/movies/%s'


# Class: Collectorz
class Collectorz(object):
    # Init
    def __init__(self):
        logger.info('Initializing Collectorz')

        self.html_parser = HTMLParser()
        self.session = Session()



    # Request
    def request(self, path, data={}, headers={}):
        # Request
        logger.info('Requesting path=%s' % (path))
        r = self.session.get(path, data=data, headers=headers)

        return r.text.encode('utf-8')


    # Search
    def search(self, query):
        logger.info('Searching movie by title "%s"' % (query))

        films = []

        query = self.html_parser.unescape(query)
        czsoup = soup(self.request(SEARCH_URL % (query)), BS_HTML_PARSER)
        results = czsoup.find('table').find_all('tr')#, class_='result_list')

        for result in results:
            if result.find('a'):
                year = result.find_all('td')[2].text
                poster = result.find('img')
                poster = poster.get('src') if poster else None
                poster = poster if 'placeholder' not in poster else None

                films.append({
                    'slug': result.find('a').get('href'), 
                    'title': result.find('a').text, 
                    'year': int(year) if year else None,
                    'poster': poster
                })

        logger.info('Found %d results' % (len(films)))

        return films


    # Barcodes
    def barcodes(self, slug):
        logger.info('Fetching barcodes for movie "%s"' % (slug))

        barcodes = []
        ignored = 0

        czsoup = soup(self.request(FILM_URL % (slug)), BS_HTML_PARSER)
        editions = czsoup.find('table', class_='table-edition')

        if not editions:
            logger.warning('No barcodes found')
            return barcodes

        for edition in editions.find_all('tr')[1:]:
            barcode = edition.find('td', class_='barcode').text

            # Ignore unknown countries
            countries = dict(MEDIA_EAN_COUNTRIES).keys()
            
            if barcode[0:3] not in countries and barcode[0:2] not in countries:
                ignored += 1
                continue
            
            media_format = edition.find('td', class_='format').find('img')
            media_format = media_format.get('alt') if media_format else None
            if media_format:
                media_format = media_format.lower()
                media_format = media_format.replace('blu-ray', 'br')
                media_format = media_format.replace('4k uhd', 'uhd')
            
            # Ignore barcoodes not of type DVD, BR, UHD
            if media_format and media_format not in ['dvd', 'br', 'uhd']:
                ignored += 1
                continue

            regions = edition.find('td', class_='regions').text
            
            release = edition.find('td', class_='released').text
            if release:
                try:
                    release = parse(release)
                    release = release.strftime('%Y-%m-%d')
                except:
                    release = None
            edition = edition.find('td', class_='edition').text

            barcodes.append({
                'barcode': barcode,
                'media_format': media_format,
                'region': regions,
                'release': release,
                'edition': edition
            })

        logger.info('Returning %d/%d barcodes' % (len(barcodes), ignored))

        return barcodes



if __name__ == '__main__':
    c = Collectorz()
    print(c.search('Blind'))
    # print c.barcodes('blind-2014')


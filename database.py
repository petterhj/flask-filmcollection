#!/usr/bin/python
# -*- coding: utf-8 -*-

# Imports
from os import path
from flask import abort
from peewee import *
from loguru import logger
from playhouse.sqlite_ext import SqliteExtDatabase#, FTSModel, RowIDField, SearchField
from playhouse.shortcuts import model_to_dict
# from playhouse.sqliteq import SqliteQueueDatabase
from requests import get
from shutil import copyfileobj

from lib.tmdb import TMDb
from lib.letterboxd import Letterboxd
from lib.collectorz import Collectorz
from config import *


# Libraries
# tmdbsimple.API_KEY = TMDB_API_KEY
# tmdb_search = tmdbsimple.Search()
# html_parser = HTMLParser()
tmdb = TMDb(TMDB_API_KEY)
collectorz = Collectorz()


# Database
db = SqliteExtDatabase(DATABASE_FILE, **{
    'pragmas': {
        'journal_mode': 'off',
    #     'cache_size': 10000,  # 10000 pages, or ~40MB
    #     'foreign_keys': 1,  # Enforce foreign-key constraints
    },
    # 'check_same_thread': False
})


# Model: Base
class BaseModel(Model):
    class Meta:
        database = db


    def to_dict(self, update={}, extra=[]):
        dict_repr = model_to_dict(self, **{
            'extra_attrs': extra
        })
        dict_repr.update(update)
        return dict_repr


    @classmethod
    def get_or_404(cls, *args, **kwargs):
        try:
            obj = cls.get(*args, **kwargs)
        except DoesNotExist:
            logger.error('Object does not exist')
        else:
            return obj
        abort(404)

    
    @classmethod
    def get_or_none(cls, *args, **kwargs):
        try:
            obj = cls.get(*args, **kwargs)
        except DoesNotExist:
            logger.error('Object does not exist')
        else:
            return obj
        return None



# Model: Film
class Film(BaseModel):
    # Fields
    pk = AutoField()
    slug = CharField(max_length=100, unique=True)
    title = CharField(max_length=100)
    release = DateField(null=True)
    original_title = CharField(max_length=100, null=True)
    original_language = CharField(max_length=3, null=True)
    overview = TextField(null=True)
    # vote_average = DecimalField(null=True)
    backdrop_path = CharField(max_length=100, null=True)
    tmdb_id = IntegerField(unique=False, null=True)


    # Search metadata
    def search_metadata(self):
        logger.info('Searching metadata for %s (%d)' % (self.slug, self.pk))

        results = tmdb.search(title=self.title)

        if len(results) == 0:
            logger.warning('No metadata matches found')
            return []

        logger.info('Found %d possible metadata matches' % (len(results)))
        return results


    # Update metadata
    def update_metadata(self, tmdb_id=None, save=True):
        logger.info('Updating metadata for %s (%d)' % (self.slug, self.pk))

        if not tmdb_id:
            metadata = self.search_metadata()

            if not metadata:
                return False

            tmdb_id = metadata[0].get('id') # Default to first match

        # Get details
        details = tmdb.metadata(tmdb_id=tmdb_id)

        if not details:
            return False
                    
        logger.info('Updating matched metadata: %s (%d)' % (
            details.get('title'), details.get('id')
        ))

        # Update instance
        try:
            self.overview = details.get('overview')
            self.release = details.get('release_date')
            self.original_title = details.get('original_title')
            self.original_language = details.get('original_language')
            self.overview = details.get('overview')
            self.vote_average = details.get('vote_average')
            self.backdrop_path = details.get('backdrop_path')
            # print self.backdrop_path
            self.tmdb_id = details.get('id')
            
            if save:
                self.save()

        except:
            logger.exception('Could not save details to database')
            return False

        # Save poster
        if not details.get('poster_path'):
            logger.warning('No poster available')

        else:
            try:
                poster_file = path.join(POSTER_PATH, '%s.jpg' % (self.slug))

                logger.info('Saving poster to %s' % (poster_file))

                r = get(TMDB_POSTER_URL % (details.get('poster_path')), stream=True)
                r.raise_for_status()
                
                if save:
                    with open(poster_file, 'wb') as f:
                        r.raw.decode_content = True
                        copyfileobj(r.raw, f)
            except:
                logger.exception('Could not save poster')

        return True

    
    # Search barcodes
    def search_barcodes(self):
        logger.info('Searching barcodes for %s (%d)' % (self.slug, self.pk))

        try:
            results = collectorz.search(query=self.title)
            slugs = [r.get('slug') for r in results]

            if self.original_title and self.original_title != self.title:
                for result in collectorz.search(query=self.original_title):
                    if result.get('slug') not in slugs:
                        results.append(result)

        except:
            logger.exception('Could not fetch barcode details')

        else:
            if len(results) > 0:
                logger.info('Found %d possible barcode matches' % (len(results)))
                return results
            else:
                logger.warning('No barcode matches found')

        return []


    # Update barcodes
    def update_barcodes(self, cz_slug=None, save=True):
        logger.info('Updating barcodes for %s (%d)' % (self.slug, self.pk))

        if not cz_slug:
            matches = self.search_barcodes()

            if not matches:
                return False

            cz_slug = matches.keys()[0]   # Default to first match

        barcodes = collectorz.barcodes(slug=cz_slug)

        if len(barcodes) == 0:
            return False

        logger.info('Adding %d barcodes to database' % (len(barcodes)))

        with db.atomic():
            for barcode in barcodes:
                try:
                    if save:
                        logger.debug('Creating barcode %s' % (barcode.get('barcode')))
                        Barcode.create(film=self, **barcode)
                except:
                    logger.exception('Could not add barcode')

        return True


    # Property: Year
    @property
    def year(self):
        if not self.release:
            return

        try:
            return self.release.year
        except:
            return int(self.release.split('-')[0])


    # Property: Copy count
    @property
    def copy_count(self):
        return len(self.copies)


    # Property: Barcode count
    @property
    def barcode_count(self):
        return len(self.barcodes)


    # Property: Poster path
    @property
    def poster_path(self):
        poster = 'assets/posters/%s.jpg' % (self.slug)
        return 'posters/%s.jpg' % (self.slug) if path.isfile(poster) else None


    # Property: Is scandinavian
    @property
    def is_scandinavian(self):
        return self.original_language in ['no', 'nb', 'sv', 'da']


    # Property: Sort title
    @property
    def sort_title(self):
        if not self.is_scandinavian or not self.original_title:
            return self.title
        return self.original_title


    # Dict representation
    def as_dict(self, copies=False, barcodes=False):
        film = model_to_dict(self, **{
            'exclude': ['overview'],
            'extra_attrs': [
                'poster_path', 'is_scandinavian', 'sort_title', 
                'year', 'copy_count', 'barcode_count'
            ]
        })
        if copies:
            film.update({
                'copies': [
                    c.as_dict(film=False) for c in Copy.select().where(Copy.film == self)
                ]
            })
        if barcodes:
            codes = [
                b.as_dict() for b in Barcode.select().where(Barcode.film == self)
            ]

            # codes.sort(key=lambda x: x['format'], reverse=True)
            codes.sort(key=lambda x: x['country'], reverse=True)

            film.update({
                'barcodes': codes
            })
        return film
    


# Model: Barcode
class Barcode(BaseModel):
    # Fields
    pk = AutoField()
    film = ForeignKeyField(Film, backref='barcodes')
    barcode = CharField(max_length=30, unique=True)
    media_format = CharField(max_length=3, choices=MEDIA_FORMATS, null=True)
    region = CharField(max_length=5, null=True)
    edition = CharField(max_length=30, null=True)
    release = DateField(null=True)


    # Property: Country
    @property
    def country(self):
        countries = dict(MEDIA_EAN_COUNTRIES).keys()
        if self.barcode[0:3] in countries:
            return dict(MEDIA_EAN_COUNTRIES).get(self.barcode[0:3])
        if self.barcode[0:2] in countries:
            return dict(MEDIA_EAN_COUNTRIES).get(self.barcode[0:2])
        return None


    # Property: Copy count
    @property
    def copy_count(self):
        return len(self.copies)
    

    # Dict representation
    def as_dict(self):
        return {
            'film': self.film.slug,
            'barcode': self.barcode,
            'format': self.media_format,
            'region': self.region,
            'country': self.country,
            'edition': self.edition,
            'release': self.release,
            'copies': self.copy_count,
        }



# Model: Copy
class Copy(BaseModel):
    # Fields
    pk = AutoField()
    film = ForeignKeyField(Film, backref='copies')
    media_format = CharField(max_length=3, choices=MEDIA_FORMATS)
    barcode = ForeignKeyField(Barcode, backref='copies', null=True)
    distributor = CharField(max_length=10, choices=MEDIA_DISTRIBUTORS, null=True)
    catalogue_number = CharField(max_length=10, null=True)


    # Set barcode
    def set_barcode(self, barcode):
        # Check if exists
        barcode_instance = Barcode.get_or_none(barcode=barcode, film=self.film)

        if not barcode_instance:
            # Create new barcode instance
            try:
                barcode_instance = Barcode.create(barcode=barcode, film=self.film)
            except:
                logger.exception('Could not create new barcode')
                return False

        self.barcode = barcode_instance
        self.save()
        return True


    # Set distributor
    def set_distributor(self, distributor, catalogue_number):
        if distributor not in dict(MEDIA_DISTRIBUTORS).keys():
            return
        if catalogue_number and len(catalogue_number) > 10:
            return

        self.distributor = distributor
        self.catalogue_number = catalogue_number.upper() if catalogue_number else None
        self.save()


    @property    
    def distributor_name(self):
        return dict(MEDIA_DISTRIBUTORS).get(self.distributor)

    
    # Dict representation
    def as_dict(self, film=True, barcodes=True):
        copy_dict = model_to_dict(self, **{
            'extra_attrs': ['distributor_name'],
            'recurse': False
        })
        copy_dict.update({
            'barcode': self.barcode.barcode if self.barcode else None,
            'country': self.barcode.country if self.barcode else None
        })
        if film:
            copy_dict.update({'film': self.film.as_dict(barcodes=barcodes)})
        return copy_dict


# Connect
db.connect()


def sync():
    added_films = []
    added_copies = []
    removed_copies = []
    updated_metadata = []

    logger.info('Syncing collection (%d lists)' % (len(LB_LISTS)))

    lb = Letterboxd(LB_USERNAME, LB_PASSWORD)

    for media_format, list_name in LB_LISTS:
        # Check if known format
        if media_format not in [f[0] for f in MEDIA_FORMATS]:
            logger.error('Unknown media format "%s", skipping!' % (media_format))
            continue

        # Get films from Letterboxd list
        films = lb.list(list_name)

        if not films or len(films) == 0:
            logger.warning('No films found in list "%s", skipping!' % (list_name))
            continue

        logger.info('Found %d films in list "%s"' % (len(films), list_name))

        # Add missing films and copies to database
        for slug, film in films.iteritems():
            # Add film
            try:
                dbf = Film.get(slug=slug)
            except DoesNotExist:
                logger.info('Adding %s to database' % (slug))
                dbf = Film.create(**{
                    'slug': slug,
                    'title': film.get('title')
                })
                added_films.append({'pk': dbf.pk, 'slug': dbf.slug})

            # Add as copy
            try:
                dbc = Copy.get(film=dbf, media_format=media_format)
            except DoesNotExist:
                logger.info('Adding copy of %s (%s) to database' % (slug, media_format))
                dbc = Copy.create(**{
                    'film': dbf,
                    'media_format': media_format
                })
                added_copies.append({'pk': dbc.pk, 'slug': dbf.slug})

        # Clean copies (delete any removed from Letterboxd)
        copies = Copy.select(Copy.pk, Copy.film).where(Copy.media_format == media_format)

        for cpk, slug in [(c.pk, c.film.slug) for c in copies]:
            if slug not in films.keys():
                logger.warning('Deleting copy of "%s" (%s)' % (slug, media_format))
                dbc = Copy.get(Copy.pk == cpk)
                removed_copies.append({'pk': dbc.pk, 'slug': dbc.film.slug})
                dbc.delete_instance()


    # Update metadata
    missing_metadata = Film.select().where(Film.tmdb_id == None)

    logger.info('Updating metadata (%d films)' % (len(missing_metadata)))

    # TMDB
    for film in missing_metadata:
        saved = film.update_metadata()
        
        if saved:
            updated_metadata.append({'pk': film.pk, 'slug': film.slug})


    logger.info('Films added: %d' % (len(added_films)))
    logger.info('Copies added: %d' % (len(added_copies)))
    logger.info('Copies removed: %d' % (len(removed_copies)))
    logger.info('Films updated: %d' % (len(updated_metadata)))
    
    return {
        'added_films': added_films, 
        'added_copies': added_copies, 
        'removed_copies': removed_copies,
        'updated_metadata': updated_metadata
    }



if __name__ == '__main__':
    # print ''

    # db.create_tables([Film, Barcode, Copy])

    # Film.create(**{
    #     'slug': 'blind-2014', 
    #     'title': 'Blind', 
    #     'release': '2014-02-28',
    #     'original_title': 'Blind',
    #     'original_language': 'no',
    #     'overview': 'Having recently lost her sight, Ingrid retreats to the safety of her home—a place where she can feel in control, alone with her husband and her thoughts. After a while, Ingrid starts to feel the presence of her husband in the flat when he is supposed to be at work. At the same time, her lonely neighbor who has grown tired of even the most extreme pornography shifts his attention to a woman across the street. Ingrid knows about this but her real problems lie within, not beyond the walls of her apartment, and her deepest fears and repressed fantasies soon take over.',
    #     'vote_average': 6.1,
    #     'tmdb_id': 245844
    # })
    # Film.create(**{
    #     'slug': 'certified-copy', 
    #     'title': 'Certified Copy', 
    #     'release': '2009-01-01',
    #     'tmdb_id': 123456
    # })



    # f = Film.get(Film.pk == 302)
    # print f.title, f.tmdb_id, f.original_title

    # for r in f.search_metadata():
    #     print r.get('title'), r.get('id')

    # print f.update_metadata(tmdb_id=16869, save=True)





    # results = f.search_metadata()
    # results = tmdb_search.movie(query='the return').get('results')
    # results = tmdb_search.movie(query='the return').get('results')

    # for f in results:
    #     print f.get('title'), f.get('release_date'), f.get('id')

    # response = tmdb_search.Movies(11190).info()
    # print f.

    # print tmdb.search(title='the return')
    # import json
    # print json.dumps(tmdb.metadata(tmdb_id=11190), indent=4)




    # print f.search_barcodes()
    # print f.search_barcodes('copie-conforme-2009')
    # print f.update_barcodes('the-return')
    
    '''
    print f.title
    for copy in f.copies:
        print copy, copy.media_format
    for copy in f.barcodes:
        print copy, copy.media_format
    '''
    # Barcode()

    # print f.search_metadata()
    # print f.update_metadata(tmdb_id=122)

    # print f.title, f.release.year
    # for bc in f.barcodes:
    #     print '-', bc.barcode

    # Barcode.create(**{
    #     'film': f,
    #     'barcode': '5021866512303',
    #     'media_format': 'dvd',
    #     'region': 2,
    #     'edition': None,
    #     'release': '2011-01-17',
    # })

    # Copy.create(**{
    #     'film': f,
    #     'media_format': 'dvd',
    #     'barcode': bc,
    #     'distributor': None,
    #     'catalogue_number': None,
    # })

    # q = Film.select(Film.title, fn.COUNT(Copy.pk).alias('copy_count'))
    # for f in q:
    #     print f.title#, len(f.copies)



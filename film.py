# Imports
from HTMLParser import HTMLParser
from requests import get


# Consntats
LB_API_URL              = 'http://petterhj.net/api/letterboxd/list/petterhj/%s'
LB_API_WATCHLIST_URL    = 'http://petterhj.net/api/letterboxd/watchlist'



# Class: FilmCollection
class FilmCollection(object):
    # Init
    def __init__(self):
        self.html_parser = HTMLParser()


    # Get collection
    def get_collection(self):
        print 'Updating collection'

        for letterboxd_list in ['collection-dvd', 'collection-bluray'] :
            self.collection += self.get_list(letterboxd_list, CollectedFilm)

        # Check if arthaus
        arthaus = [f.slug for f in self.get_list('collection-arthaus')]

        for film in self.collection:
            if film.slug in arthaus:
                film.is_arthaus = True


    # Get list
    def get_list(self, list_name, film_type=None):
        # Films
        films = []

        try:
            film_type = film_type if film_type else Film
            request = get(LB_API_URL % (list_name)).json()
            
            if not request['response']['success']:
                raise Exception('Could not get list data')

            for slug, film in request['response']['result'].iteritems():
                films.append(film_type(**{
                    'slug': slug,
                    'title': self.html_parser.unescape(film['title']), 
                    'year': film['year'],
                    'list_name': list_name
                }))

        except Exception as e:
            print '[FILMCOLLECTION] error: %s' % (str(e))

        # else:
        #     films = sorted(films, key=lambda k: k['sort_title']) 

        print '> %d films found in %s' % (len(films), list_name)

        return films



# Class: Film
class Film(object):
    # Init
    def __init__(self, slug, title, year, list_name):
        # Properties
        self.slug = slug
        self.title = title
        self.year = year
        self.list_name = list_name


    # String representation
    def __str__(self):
        return '<%s [%s]%s: %s (%s)>' % (
            self.__class__.__name__, self.slug, '[A]' if self.is_arthaus else '',
            self.title, self.year
        )



# Class: CollectedFilm
class CollectedFilm(Film):
    # Init
    def __init__(self, slug, title, year, list_name):
        # Super
        super(CollectedFilm, self).__init__(slug, title, year, list_name)

        # Properties
        self.is_arthaus = False



if __name__ == '__main__':
    fc = FilmCollection()

    # films = fc.get_list('collection-arthaus')
    for f in fc.get_collection()[0:10]:
        print f
# Imports
from peewee import *
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import check_password_hash

import config
from database import Film, Barcode, Copy, sync as db_sync


# App
app = Flask(__name__, template_folder='assets', static_folder='assets')

app.config.update(
    DEBUG = config.APP_DEBUG,
    SECRET_KEY = config.APP_SECRET_KEY
)


# Authentication
class User(UserMixin):
    id = config.APP_USER
    username = config.APP_USER

    def check_password(self, password):
        return check_password_hash(config.APP_PASS_HASH, password)


login = LoginManager(app)

@login.user_loader
def load_user(id):
    return User()


# Route: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = load_user(None)

        if request.form['username'] == user.username and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('index'))

        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')


# Route: Logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# Route: Index
@app.route('/')
def index():
    # copies = [c.as_dict() for c in Copy.select()]
    copies = [c.as_dict() for c in Copy.select().order_by(Copy.pk.desc()).limit(15)]
    # copies = [c.as_dict() for c in Copy.select().order_by(fn.Random()).limit(13)]
    # copies = [c.as_dict() for c in Copy.select().where(Copy.media_format.contains('br')).limit(100)][40:50]
    # copies = [c.as_dict() for c in Copy.select().where(Copy.catalogue_number.contains('DVD'))]
    # copies = [c.as_dict() for c in Copy.select().where(Copy.catalogue_number.contains('DVD'))]
    copies = sorted(copies, key=lambda x: x['film']['sort_title'])
    return render_template('index.html', copies=copies)


# Route: Dicover
@app.route('/discover')
def discover():
    # Render template
    return render_template('discover.html')


# JSON: Films
@app.route('/json/films/')
def films():
    # Return films
    return jsonify({'films': [f.as_dict() for f in Film.select()]})


# JSON: Film
@app.route('/json/film/<slug>/')
def film(slug):
    # Return film
    return jsonify({'film': Film.get(slug=slug).as_dict(copies=True, barcodes=True)})


# JSON: Copies
@app.route('/json/collection/copies')
def copies():
    # Return copies
    return jsonify({'copies': [c.as_dict() for c in Copy.select()]})


# JSON: Copy
@app.route('/json/collection/copy/<copy_pk>/')
def copy(copy_pk):
    return jsonify({
        'copy': Copy.get_or_404(pk=copy_pk).as_dict()
    })


# JSON: Random copy
@app.route('/json/collection/copy/random')
def random_copy():
    # Return copies
    random_copy = Copy.select().order_by(fn.Random()).limit(1).get()
    return jsonify({'copy': random_copy.as_dict()})



# JSON: Sync collection
@app.route('/json/collection/sync')
@login_required
def sync():
    '''
    Sync Letterboxd collection.
    '''
    return jsonify({'result': db_sync()})


# JSON: Update film(s) metadata
@app.route('/json/films/update/')
@app.route('/json/film/<slug>/update/')
@login_required
def films_update(slug=None):
    '''
    Return list of films missing metadata. If a slug is provided, 
    return requested film for update.
    '''

    films = []

    query = Film.select().where(Film.slug == slug if slug else Film.tmdb_id.is_null(True))
    
    for film in query:
        films.append({
            'film': film.to_dict(extra=['year']),
            'metadata': film.search_metadata(),
            'barcodes': film.search_barcodes()
        })

    return jsonify({'films': films})


# JSON: Update film metadata
@app.route('/json/film/<slug>/update/metadata/<tmdb_id>/')
@login_required
def film_update_metadata(slug, tmdb_id):
    # Update film metadata
    film = Film.get(slug=slug)
    film.update_metadata(tmdb_id, save=True)
    return jsonify({'film': film.as_dict()})


# JSON: Update film barcodes
@app.route('/json/film/<slug>/update/barcodes/<barcode_slug>/')
@login_required
def film_update_barcodes(slug, barcode_slug):
    # Update film barcodes
    film = Film.get(slug=slug)
    film.update_barcodes(barcode_slug, save=True)
    return jsonify({'film': film.as_dict()})


# JSON: Update copy barcode
@app.route('/json/collection/copy/<copy_pk>/barcode/<barcode>/')
@login_required
def copy_update_barcode(copy_pk, barcode):
    # Get copy and barcode
    copy = Copy.get_or_404(pk=copy_pk)

    copy.set_barcode(barcode)

    return jsonify({'copy': copy.as_dict()})


# JSON: Update copy distributor
@app.route('/json/collection/copy/<copy_pk>/distributor/<distributor>/')
@app.route('/json/collection/copy/<copy_pk>/distributor/<distributor>/<catalogue_number>/')
@login_required
def copy_update_distributor(copy_pk, distributor, catalogue_number=None):
    copy = Copy.get_or_404(pk=copy_pk)

    copy.set_distributor(distributor, catalogue_number)

    return jsonify({'copy': copy.as_dict()})


# JSON: Distributors
@app.route('/json/distributors/')
@login_required
def distributors():
    # Return barcodes
    return jsonify({'distributors': [{
            'code': d[0],
            'name': d[1]
        } for d in list(config.MEDIA_DISTRIBUTORS)]})


# # JSON: Barcodes
# @app.route('/json/barcodes')
# def barcodes():
#     # Return barcodes
#     return jsonify({'barcodes': {b.barcode: b.as_dict() for b in Barcode.select()}})

# @app.route('/json/collection/barcodes')
# def collected_barcodes():
#     # Return barcodes
#     barcodes = Copy.select().where(Copy.barcode.is_null(False))
#     return jsonify({'barcodes': {
#         c.barcode.barcode: c.film.slug for c in barcodes
#     }})



# Main
if __name__ == "__main__":
    # app.debug = config.APP_DEBUG
    app.run(host=config.APP_HOST, port=config.APP_PORT)
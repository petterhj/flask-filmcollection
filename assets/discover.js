// Get films
var films = [];
var discovered = [];

function update_details(film) {
    // Film data
    $('div.title > span.title').text((film.is_scandinavian ? film.original_title : film.title));
    $('div.title > span.year').text('(' + film.year + ')');
    if (film.original_title && (film.original_title != film.title)) {
        $('div.alt_title').text((film.is_scandinavian ? film.title : film.original_title)).show();
    } else { $('div.alt_title').hide(); }
    $('div.overview').text(film.overview);

    $('div.meta > span.format').text(film.list_type);
    if (film.is_arthaus) {
        $('div.meta > span.arthaus').text('ARTHAUS').show();
    } else { $('div.meta > span.arthaus').hide(); }
    $('div.meta > span.language').text(film.original_language);
    $('div.meta > span.rating').text(film.vote_average);

    $('div.loading').hide();
    $('div.film').fadeIn();
}

function random_film() {
    $('div.loading').fadeIn();

    console.log('Chosing random film (' + films.length + ' available)...');

    if (films.length > 0) {
        var index = -1;

        while ((index < 0) || discovered.includes(index)) {
            index = Math.floor(Math.random() * films.length);
        }

        discovered.push(index);

        var film = films[index];

        console.log(film);
        console.log(film.backdrop_path);

        // Set backdrop
        if (film.backdrop_path) {
            var img = new Image();
            img.onload = function() {
                update_details(film);
                $('section#discover').css({
                    backgroundImage: 'url("' + img.src + '")',
                });
            };
            img.src = film.backdrop_path;
        } else {
            update_details(film);
            $('section#discover').css({
                backgroundImage: 'none',
            });
        }

    } else {
        console.log('No films available');
    }
}

$(document).ready(function() {
    $('div.loading').fadeIn();

    $.getJSON('/filmcollection/films', function(data) {
        films = data.films;

        random_film();

        $('section#discover').click(function() {
            random_film();
        });
    });
}).keydown(function(e) {
    switch(e.which) {
        case 39: // right
            random_film();
            break;

        default: return;
    }
    e.preventDefault();
});
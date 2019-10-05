/*  Utilities
================================================================================== */

// String format
if (!String.prototype.format) {
    String.prototype.format = function() {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function(match, number) { 
            return typeof args[number] != 'undefined' ? args[number] : match;
        });
    };
}

// Handlebars helper: Truncate
Handlebars.registerHelper('truncate', function (str, len) {
    if (str.length > len && str.length > 0) {
        var new_str = str + " ";
        new_str = str.substr (0, len);
        new_str = str.substr (0, new_str.lastIndexOf(" "));
        new_str = (new_str.length > 0) ? new_str : str.substr (0, len);

        return new Handlebars.SafeString ( new_str +'...' ); 
    }
    return str;
});

// Handlebars helper: Uppercase
Handlebars.registerHelper('uppercase', function (str) {
    return str.toUpperCase();
});

// Handlebars helper: Count
Handlebars.registerHelper('count', function (arr) {
    return arr.length;
});

// Handlebars helper: Metadata match
Handlebars.registerHelper('metadata_match', function(existing_tmdb_id, tmdb_id) {
    return (existing_tmdb_id === tmdb_id ? 'matched' : '');
});


/*  App
================================================================================== */

APP = {
    site: COLLECTION,
    
    // Execute
    exec: function(view) {
        var ns = this.site;
        var views = ns.views;
        var view = (view === undefined) ? 'common' : view;

        if (view && typeof views[view] == 'function') {
            console.log('View:' + view);
            views[view]();
        }
    },
 
    // Start
    start: function() {
        var body = document.body,
            view = body.getAttribute('data-view'),
            admin = (body.getAttribute('data-admin') === 'true' ? true : false);
        
        APP.site.options.admin = admin;
        APP.exec('common');
        APP.exec(view);
    },
    
    // Log
    log: function(message) {
        if (this.site.options.debug) {
            console.log('[' + this.site.options.name + '] ' + message);
        }
    }
};


/*  Initialize
  ================================================================================== */

$(document).ready(APP.start);

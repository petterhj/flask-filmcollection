// COLLECTION
var COLLECTION = COLLECTION || {
    // Options
    options: {
    	name: 'FC',
        debug: true,
        admin: false,
    },

    // Show update modal
    showUpdateModal: function(slug) {
    	var template = Handlebars.compile($('#find_metadata_template').html());
    	var url = (slug ? '/json/film/{0}/update'.format(slug) : '/json/films/update');

	    vex.open({
	        unsafeContent: 'Søker...',
	        afterOpen: function() {
	            var content_element = $(this.contentEl);
	            var close_button = content_element.find('.vex-close');

				$.getJSON(url, function(data) {
	                var rendered = $(template(data));
	                content_element.html(rendered).append(close_button);

	                // Select metadata match
	                rendered.find('.film[data-tmdb-id]').on('click', function(e) {
	                	var match = $(this),
	                		slug = match.parent().parent().data('slug'),
	                		film_pk = match.parent().parent().data('film-pk'),
	                		tmdb_id = match.data('tmdb-id'),
	                		film = $('div.copy[data-film-pk="{0}"]'.format(film_pk));

	                	APP.log('Selecting metadata match, id={0}'.format(tmdb_id));

	                	match.off('click');
	                	match.parent().find('.film[data-tmdb-id]').not(match).fadeOut();
	                	match.addClass('selected').find('p').fadeOut();

	                	// Update metadata
	                	$.getJSON('/json/film/{0}/update/metadata/{1}/'.format(slug, tmdb_id), function(result) {
	                		match.addClass('updated');
	                		film.find('div.title').html(result.film.title)
	                			.append($('<span>', {class: 'og_title'}).text(result.film.original_title));
	                		film.find('div.year').text(result.film.year);

	                		if (result.film.poster_path) {
	                			console.log(result.film.poster_path);
	                			film.find('img.poster').attr('src', '/assets/{0}?id={1}'.format(
	                				result.film.poster_path, result.film.tmdb_id
	                			));
	                		}
	                	});
	                });

	                // Manual metadata update
	                rendered.find('input[name="metadata_manual"]').on('keypress', function(e) {
                		if ((e.which != 13) || ($(this).val().length < 4)) {
                			return;
                		}

	                	var slug = $(this).parent().parent().data('slug'),
	                		film_pk = $(this).parent().parent().data('film-pk'),
	                		tmdb_id = $(this).val(),
	                		film = $('div.copy[data-film-pk="{0}"]'.format(film_pk));

                		// Update metadata
                		console.log('/json/film/{0}/update/metadata/{1}/'.format(slug, tmdb_id));
	                	$.getJSON('/json/film/{0}/update/metadata/{1}/'.format(slug, tmdb_id), function(result) {
	                		console.log(result);
	                		film.find('div.title').html(result.film.title)
	                			.append($('<span>', {class: 'og_title'}).text(result.film.original_title));
	                		film.find('div.year').text(result.film.year);
	                		if (result.film.poster_path) {
	                			film.find('img.poster').attr('src', '/assets/{0}'.format(result.film.poster_path));
	                		}
	                	});
                	});

	                // Select barcode match
	                rendered.find('.barcodes[data-barcode-slug]').on('click', function(e) {
	                	var match = $(this),
	                		slug = match.parent().parent().data('slug'),
	                		film_pk = match.parent().parent().data('film-pk'),
	                		barcode_slug = match.data('barcode-slug'),
	                		film = $('div.copy[data-film-pk="{0}"]'.format(film_pk));

	                	APP.log('Selecting barcode match, slug={0}'.format(barcode_slug));

	                	match.off('click');
	                	match.parent().find('.barcodes[data-barcode-slug]').not(match).fadeOut();
	                	match.addClass('selected').find('p').fadeOut();

	                	// Update barcodes
	                	$.getJSON('/json/film/{0}/update/barcodes/{1}/'.format(slug, barcode_slug), function(result) {
	                		APP.log('Saved {0} barcodes to database'.format(result.film.barcode_count));
	                		
	                		match.addClass((result.film.barcode_count > 0) ? 'updated' : 'warning');
	                		film.find('div.barcodes').attr('data-barcode-count', result.film.barcode_count);
	                		film.find('div.barcodes span').text(result.film.barcode_count);
	                	});
	                });

	                // Show more results
	                rendered.find('.elements').each(function() {
	                	var elements = $(this);
	                	var element_count = elements.find('.element').length;
	                	var matched_element = elements.find('.element.matched');

	                	if (matched_element.length > 0) {
	                		matched_element.prependTo(elements);
	                	}

	                	APP.log('Found {0} possible {1} matches'.format(element_count, elements.data('element-type')));

	                	if (element_count > 1) {
		                	elements.find('a.show_more').css({display: 'block'}).on('click', function(e) {
			                	e.preventDefault();
			                	$(this).hide().parent().parent().find('.element').fadeIn();
			                });
		                }
	                });
	            });
	        }
	    });
    },

    // Show barcode modal
    showBarcodeModal: function(copy_pk) {
		var template = Handlebars.compile($('#show_barcode_template').html());
		
	    vex.open({
	        unsafeContent: 'Henter strekkoder...',
	        afterOpen: function() {
	            var content_element = $(this.contentEl);
	            var close_button = content_element.find('.vex-close');

	            $.getJSON('/json/collection/copy/{0}/'.format(copy_pk), function(data) {
	                var rendered = $(template(data.copy));
	                content_element.html(rendered).append(close_button);

	                if (data.copy.barcode) {
	                	JsBarcode('svg.bc').init();
	                	content_element.find('div.barcode[data-barcode="{0}"]'.format(data.copy.barcode)).addClass('matched');
	                }
	            });
	        }
	    });
    },

    // Show barcode select modal
    showBarcodeSelectModal: function(copy_pk) {
		var template = Handlebars.compile($('#select_barcode_template').html());
		
	    vex.open({
	        unsafeContent: 'Henter strekkoder...',
	        afterOpen: function() {
	            var content_element = $(this.contentEl);
	            var close_button = content_element.find('.vex-close');

	            $.getJSON('/json/collection/copy/{0}/'.format(copy_pk), function(data) {
	                var rendered = $(template(data.copy));
	                content_element.html(rendered).append(close_button);
	                var barcode_render_options = {
                		format: 'EAN13',
                		fontOptions: 'bold',
                		textMargin: 0
            		};

	                if (data.copy.barcode) {
	                	JsBarcode('svg.bc', data.copy.barcode, barcode_render_options);
	                }

	                var stored_barcodes = data.copy.film.barcodes;
	                	stored_barcodes = Object.keys(stored_barcodes).map(function(k) { 
	                		return stored_barcodes[k]['barcode'];
	                	});
	                var barcode = content_element.find('.current_barcode');
	                var barcode_input = content_element.find('input[name="barcode"]');
	                
	                barcode_input.typeahead({
						hint: true,
						highlight: true,
						autoselect: true,
						minLength: (data.copy.barcode ? 1 : 0),
					}, {
						name: 'states',
						source: function(query, matches) {
							var barcodes = [];
							
							$.each(stored_barcodes, function(i, barcode) {
								if (barcode.indexOf(query) === 0) {
									barcodes.push(barcode);
								}
							});

							matches(barcodes)
						}
					})
					.on('keypress typeahead:selected', function(e, stored_barcode) {
						var barcode_value = $(this).val(),
							current_barcode = barcode.attr('data-current-barcode'),
            				updated_barcode = barcode.attr('data-updated-barcode'),
            				is_stored = (stored_barcode ? true : false);

						// Enter pressed or stored code selected (using typeahead)
						if ((e.which == 13 || is_stored)) {
                			APP.log('Selected bacore={0} (stored={1}), current={2}, updated={3}'.format(
                				barcode_value, is_stored, current_barcode, updated_barcode
                			));

							// Select all text in input
							barcode_input.select();
							barcode_input.toggleClass('error', (barcode_value.length !== 13));

							if (barcode_value.length !== 13) {
								APP.log('Resetting barcode to initial');
			                	barcode.removeClass('changed saved error')
			                		.attr('data-updated-barcode', '');

			                	if (current_barcode) {
									JsBarcode('svg.bc', current_barcode, {
				                		format: 'EAN13',
				                		fontOptions: 'bold',
				                		textMargin: 0
			                		});
			                	} else {
			      					$('svg.bc').html('');
			                	}

								return;
							}

							// Check if new barcode is selected
							if (updated_barcode && (barcode_value === updated_barcode)) {
								// Check if current
								if (updated_barcode === current_barcode) {
									APP.log('Nothing to update (ignore)');
									barcode.addClass('saved');
									setTimeout(function() { vex.closeAll(); }, 500);
								} else {
									APP.log('Save selected barcode, {0}'.format(updated_barcode));

									var copy = $('.copy[data-pk="{0}"]'.format(copy_pk));

				                	$.getJSON('/json/collection/copy/{0}/barcode/{1}/'.format(
				                		copy_pk, updated_barcode
				                	), function(result) {
				                		copy.attr('data-barcode', result.copy.barcode);
				                		
				                		if (result.copy.barcode === updated_barcode) {
				                			barcode.addClass('saved');
				                			setTimeout(function() { vex.closeAll(); }, 500);
				                		} else {
				                			// barcode.addClass('error');
				                			barcode_input.addClass('error');
				                			// barcode_input.select();
				                		}
				                	});
								}
							} 
							else {
								// Render new bar code
								APP.log('Selecting new barcode, {0}'.format(barcode_value));

								try {
		                			JsBarcode('svg.bc', barcode_value, barcode_render_options);
			                	} catch(err) {
			                		APP.log('Invalid barcode, {0}'.format(barcode_value));
			                		// barcode.addClass('error').attr('data-updated-barcode', '');
			                		barcode.attr('data-updated-barcode', '');
			                		barcode_input.addClass('error');
			                		return;
			                	}

			                	barcode.attr('data-updated-barcode', barcode_value);
			                	barcode.removeClass('error');
				                barcode.toggleClass('changed', (barcode_value !== current_barcode));
			                	barcode.toggleClass('stored', is_stored);
			                }
						} 
						// Keypress
						else {
							APP.log('Resetting barcode to initial');
		                	barcode.removeClass('changed saved error')
		                		.attr('data-updated-barcode', '');

		                	if (current_barcode) {
								JsBarcode('svg.bc', current_barcode, {
			                		format: 'EAN13',
			                		fontOptions: 'bold',
			                		textMargin: 0
		                		});
		                	} else {
		      					$('svg.bc').html('');
		                	}
						}
                	}).focus();
	            });
	        }
	    });
    },

    // Show distributor modal
    showDistributorModal: function(copy_pk) {
    	var template = Handlebars.compile($('#select_distributor_template').html());
		
	    vex.open({
	    	unsafeContent: 'Velg distributør...',
	        afterOpen: function() {
	            var content_element = $(this.contentEl);
	            var close_button = content_element.find('.vex-close');

				$.getJSON('/json/collection/copy/{0}/'.format(copy_pk), function(copy_data) {
	            	$.getJSON('/json/distributors/', function(distributor_data) {
		                var rendered = $(template({
		                	copy: copy_data.copy,
		                	distributors: distributor_data.distributors
		                }));
		                content_element.html(rendered).append(close_button);

		                if (copy_data.copy.distributor) {
		                	$('.element[data-distributor-code="{0}"]'.format(
		                		copy_data.copy.distributor
		                	)).addClass('selected');
		                }

		                content_element.find('input[name="catalogue_number"]').focus();

		                // Select distributor match
		                rendered.find('.distributor[data-distributor-code]').on('click', function(e) {
		                	var match = $(this),
		                		code = match.data('distributor-code'),
		                		catnum = match.parent().parent().find('input[name="catalogue_number"]').val(),
		                		copy = $('div.copy[data-pk="{0}"]'.format(copy_pk));

		                	APP.log('Selecting metadata match, code={0}, catalogue_number={1}'.format(
		                		code, catnum
		                	));

		                	match.parent().find('.element').removeClass('selected');
		                	match.off('click').addClass('selected');

		                	// Update distributor
		                	$.getJSON('/json/collection/copy/{0}/distributor/{1}/{2}'.format(copy_pk, code, catnum), function(result) {
		                		match.addClass('updated');

		                		copy.find('div.distributor').attr('data-distributor', result.copy.distributor);
		                		copy.find('div.distributor').find('i.zmdi').attr('title', result.copy.distributor_name);
		                		copy.find('div.distributor').find('span').text(result.copy.catalogue_number);

		                		setTimeout(function() { vex.closeAll(); }, 500);
		                	});
		                });
					});
	            });
	        }
	    });
    },

    // Check metadata
    checkMetadata: function() {
    	APP.log('Checking missing metadata');

    	$.getJSON('/json/films/update/', function(data) {
    		APP.log('Metadata missing for {0} film(s)'.format(data.films.length));
    		
    		if (data.films.length == 0) {
    			return;
    		}

			var n = new Noty({
				type: 'warning',
			  	text: 'Mangler metadata for {0} film(er)!'.format(data.films.length),
			  	buttons: [
			    	Noty.button('Oppdater', 'btn btn-success', function () {
			        	APP.log('Requesting metadata update modal');
			        	n.close();
			        	COLLECTION.showUpdateModal();
			    	}, {id: 'button1', 'data-status': 'ok'}),

			    	Noty.button('Ignorer', 'btn btn-error', function () {
			        	APP.log('Ignoring missing metadata');
			        	n.close();
			    	})
				]
			});
			
			n.show();
    	});
    },

    // Views
    views: {
	    // View: Common
	    common: function() {
	    	vex.defaultOptions.className = 'vex-theme-watchlist';

	    	$('div.admin').on('click', function() {
	    		window.location.href = (COLLECTION.options.admin ? '/logout' : '/login');
	    	});
	    },

	    // View: Collection
	    collection: function() {
	        // Search filter
	        $('input[name="search"]').focus().keyup(function() {
		        var data_qjs = '.films_table .title'
		        var data_qjs_bc = '.films_table .barcodes span.barcode'
		        var barcode_pattern = new RegExp('^[0-9]{13}$');
		        var search_query = $(this).val();

		        $.expr[":"].Contains = $.expr.createPseudo(function(arg) {
		            return function(elem) {
		                return $(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
		            };	
		        });

		        if (barcode_pattern.test(search_query)) {
		            $(data_qjs_bc).parent().parent().hide();
		            $(data_qjs_bc+':Contains("{0}")'.format(search_query)).parent().parent().show();
		        } else {
		            $(data_qjs).parent().hide();
		            $(data_qjs+':Contains("{0}")'.format(search_query)).parent().show();
		        }
		    });

		    $(document).keyup(function(e) {
				if (e.key === 'Escape') {
					$('input[name="search"]').val('').focus().trigger('keyup');
			    }
			});

	        // Filters
		    $('div.filter').each(function(i, filter) {
		        var filter = $(filter);
		        
		        filter.click(function() {
		            if ($(this).hasClass('all')) {
		                $('div.films_table').find('div.copy').show();
		            }
		            if ($(this).hasClass('dvd')) {      
		                $('div.films_table').find('div.copy.dvd').show();
		                $('div.films_table').find('div.copy.br').hide();
		            }
		            if ($(this).hasClass('br')) {
		                $('div.films_table').find('div.copy.br').show();
		                $('div.films_table').find('div.copy.dvd').hide();
		            }
		            if ($(this).hasClass('arthaus')) {
		                $('div.films_table').find('div.copy.arthaus').show();
		                $('div.films_table').find('div.copy').not('.arthaus').hide();
		            }
		            // if ($(this).hasClass('in_collection')) {
		            //     $('table').find('div.copy.in_collection').show();
		            //     $('table').find('div.copy').not('.in_collection').hide();
		            // }
		        });

		        if (filter.hasClass('all')) {
		            filter.append($('<span>').text($('div.copy').length));
		        }
		        else if (filter.hasClass('dvd')) {
		            filter.append($('<span>').text($('div.copy.dvd').length));
		        }
		        else if (filter.hasClass('br')) {
		            filter.append($('<span>').text($('div.copy.br').length));
		        }
		        else if (filter.hasClass('arthaus')) {
		            filter.append($('<span>').text($('div.copy.arthaus').length));
		        }
		        // if (filter.hasClass('in_collection')) {
		        //     filter.append($('<span>').text($('div.copy.in_collection').length));
		        // }
		    });

	        // Check if any missing metadata
	        if (COLLECTION.options.admin) {
				COLLECTION.checkMetadata();
			}

	        // Films
	        $('section#films div.copy').each(function() {
	        	var slug = $(this).data('slug');

	        	// Metadata
	        	if (COLLECTION.options.admin) {
		        	$('img.poster', this).on('click', function() {
		        		// Update metadata
		        		COLLECTION.showUpdateModal(slug);
		        	});

		        	// Distributor
		        	$('div.distributor', this).on('click', function() {
			        	COLLECTION.showDistributorModal($(this).parent().data('pk'));
		        	});
		        }

	        	// Barcode
	        	$('div.barcodes', this).on('click', function() {
	        		if (COLLECTION.options.admin) {
		        		// Select barcode
		        		COLLECTION.showBarcodeSelectModal($(this).parent().data('pk'));
		        	} else {
		        		COLLECTION.showBarcodeModal($(this).parent().data('pk'));
		        	}
	        	});
	        });



	        /////////////////////////////////
	        // COLLECTION.showBarcodeSelectModal(368)
	        // COLLECTION.showUpdateModal('united')

		    var baseModal = function(vex) {
		    	var modal;
			    return {
			        init: function() {
			        	console.log('Initializing modal {0}'.format(this.name));
			        	
			        	modal = this;
			        	
			        	var template = $(modal.template_selector).html()
			        	modal.template = Handlebars.compile(template);
			        },
			        render: function(instance) {
			        	// Element
			        	modal.element = $(instance.contentEl);
			        	
			        	// Fetch source data
			        	this.source_url = this.source_url.replace(/{{(\w+)}}/g, function(match, p1) {
						   return modal.options[p1];
						});

	            		var close_button = modal.element.find('.vex-close');

			            $.getJSON(this.source_url, function(data) {
			            	var rendered = $(modal.template(data.copy));
			            	modal.element.html(rendered).append(close_button);
			            	
			            	modal.onRendered(modal, data);
			            });
			    	},
			        open: function(options) {
			        	modal.options = options;
			        	
			            return vex.open({
							unsafeContent: this.name,
							afterOpen: function() {
								modal.render(this);
							}
						});
			        }
			    }
			};

			var barcodeModal = function(vex) {
		    	return $.extend({}, baseModal(vex), {
		    		name: 'barcodeModal',
		    		template_selector: '#select_barcode_template',
		    		source_url: '/json/collection/copy/{{copy_pk}}/',
		    		options: {
		    			barcode: {
							format: 'EAN13',
	                		fontOptions: 'bold',
	                		textMargin: 0
		    			},
		    			typeahead: {
							hint: true,
							highlight: true,
							autoselect: true,
							// minLength: (data.copy.barcode ? 1 : 0),
		    			}
		    		},
            		renderBarcode: function(barcode) {
            			if (!barcode)
            				return;

            			JsBarcode('svg.bc', barcode, this.options.barcode);
            		},
            		barcodeLookup: function(query, barcodes) {
						var matches = [];

						barcodes = Object.keys(barcodes).map(function(k) { 
	                		return barcodes[k]['barcode'];
	                	});
						
						$.each(barcodes, function(i, barcode) {
							if (barcode.indexOf(query) === 0) {
								matches.push(barcode);
							}
						});

						return matches;
            		},
		    		onRendered: function(modal, data) {
		    			console.log('onRender');
		    			console.log(modal.element);
		    			console.log(data);

		    			// Barcode
		                var barcode = modal.element.find('.current_barcode');

		    			modal.renderBarcode(data.copy.barcode);

		    			// Input
		    			var barcodes = data.copy.film.barcodes;
		    			var input = modal.element.find('input[name="barcode"]');

						input.typeahead(modal.options.typeahead, {
							source: function(query, matches) {
								matches(modal.barcodeLookup(query, barcodes));
							}
						})
						.on('keypress typeahead:selected', function(e, barcodes) {
							var barcode_value = $(this).val(),
								current_barcode = barcode.attr('data-current-barcode'),
	            				updated_barcode = barcode.attr('data-updated-barcode'),
	            				is_stored = (barcodes ? true : false);

	            			console.log(barcode_value);
	            			console.log(current_barcode);
	            			console.log(updated_barcode);
	            			console.log(is_stored);
						});

						input.focus();
		    		}
		    	});
		    };

			vex.registerPlugin(barcodeModal)
			vex.barcodeModal.init();

			vex.barcodeModal.open({copy_pk: 400})
	        /////////////////////////////////
	    },

	    // View: Discover
	    discover: function() {
	    	function update_details(copy) {
	    		var film = copy.film;

				$('div.title > span.title').text(film.sort_title);
	    		$('div.title > span.year').text('(' + film.year + ')');
			    if (film.original_title && (film.original_title != film.title)) {
			        $('div.alt_title').text((film.is_scandinavian ? film.title : film.original_title)).show();
			    } else { $('div.alt_title').hide(); }
			    $('div.overview').text(film.overview);

			    $('div.meta > span.format').text(copy.media_format);
			    if (copy.distributor_name) {
			        $('div.meta > span.arthaus').text(copy.distributor_name).show();
			    }// else { $('div.meta > span.arthaus').hide(); }
			    $('div.meta > span.language').text(film.original_language);
			    $('div.meta > span.rating').text(film.vote_average);

	    		$('div.loading').hide();
    			$('div.film').fadeIn();
	    	}

	    	function fetch_random() {
				// Fetch random copy from database
				APP.log('Fetching random copy from database');

		    	$.getJSON('/json/collection/copy/random', function(data) {
		    		if (data.copy.film.backdrop_path) {
			            var img = new Image();
			            img.onload = function() {
			            	update_details(data.copy);
			                $('section#discover').css({
			                    backgroundImage: 'url("' + img.src + '")',
			                });
			            };
			            img.src = 'http://image.tmdb.org/t/p/w1280/' + data.copy.film.backdrop_path;
			        } else {
			        	update_details(data.copy);
			            $('section#discover').css({
			                backgroundImage: 'none',
			            });
			        }
		    	});
	    	}

	    	fetch_random();

	    	$('section#discover').click(function() {
            	fetch_random();
        	});
	    }
	}
}
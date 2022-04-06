import { current } from 'daisyui/src/colors'
import { defineStore } from 'pinia'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export const useFilmStore = defineStore('film', {
  state: () => ({
    film: null,
    searchResults: [],
    // selectedSearchResult: null,
    isSearching: null,
    isUpdating: null,
    filmPatch: {
      imdb_id: null,
      title: null,
      display_title: null,
    },
  }),

  getters: {
    isPatched(state) {
      const currentFilm = {
        imdb_id: state.film.imdb_id,
        title: state.film.title,
        display_title: state.film.display_title,
      }
      console.log("current", JSON.stringify(currentFilm))
      console.log("patch", JSON.stringify(state.filmPatch))
      return (
        JSON.stringify(currentFilm) !== JSON.stringify(state.filmPatch)
      )
    },
  },

  actions: {
    searchMetadata() {
      if (!this.film)
        return
      console.log(`Searching IMDB, slug="${this.film.lb_slug}"`)
      this.isSearching = true
      fetch(`${API_BASE_URL}/films/${this.film.lb_slug}/search`)
        .then(response => response.json())
        .then(data => {
          this.searchResults = data
          console.log(`Got ${this.searchResults.length} result(s)`)
          if (this.searchResults.length > 0) {
            this.filmPatch.imdb_id = this.searchResults[0].imdb_id
          }
        })
        .catch((error) => console.log(error))
        .finally(() => this.isSearching = false)
    },
    refreshMetadata(imdb_id) {
      console.log(`Refreshing ${this.film.lb_slug} metadata with IMDB ID ${imdb_id}`)
      fetch(`${API_BASE_URL}/films/${this.film.lb_slug}/refresh?imdb_id=${imdb_id}`)
        .then(response => response.json())
        .then(data => {
          this.film = data
          // this.films = this.films.map((film) => {
          //   if (film.lb_slug === data.lb_slug) {
          //     return data
          //   }
          //   return film
          // })
        })
        .catch((error) => console.log(error))
    }
  },
})

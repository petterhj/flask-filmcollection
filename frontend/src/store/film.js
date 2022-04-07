import { defineStore } from 'pinia'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export const useFilmStore = defineStore('film', {
  state: () => ({
    film: null,
    searchResults: [],
    // selectedSearchResult: null,
    isSearching: null,
    isUpdating: null,
    metadataPatch: {
      imdb_id: null,
      title: null,
      display_title: null,
    },
  }),

  getters: {
    patchable: (state) => ({
      imdb_id: state.film.imdb_id,
      title: state.film.title,
      display_title: state.film.display_title,
    }),
    hasPatchedMetadata(state) {
      // console.log("current", JSON.stringify(this.patchable))
      // console.log("patch", JSON.stringify(state.metadataPatch))
      return (
        JSON.stringify(this.patchable) !== JSON.stringify(state.metadataPatch)
      )
    },
    selectedMetadataSource: (state) => state.searchResults.find(result => (
      result.imdb_id === state.metadataPatch.imdb_id
    ))
  },

  actions: {
    searchMetadata() {
      console.log(`Searching IMDB, slug="${this.film.lb_slug}"`)
      this.isSearching = true
      // this.filmPatch.imdb_id = (this.film.imdb_id ? this.film.imdb_id : null)
      fetch(`${API_BASE_URL}/films/${this.film.lb_slug}/search`)
        .then(response => response.json())
        .then(data => {
          this.searchResults = data
          console.log(`Got ${this.searchResults.length} result(s)`)
          // if (!this.filmPatch.imdb_id && this.searchResults.length > 0) {
          //   this.filmPatch.imdb_id = this.searchResults[0].imdb_id
          // }
        })
        .catch((error) => console.log(error))
        .finally(() => this.isSearching = false)
    },
    saveMetadata(filmPatch) {
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
    },
    setMetadataPatch(data) {
      Object.keys(data).forEach((key) => {
        if (key in metadataPatch)
            this.metadataPatch[key] = data[key];
      })
    }
  },
})

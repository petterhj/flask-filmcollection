import { defineStore } from 'pinia'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export const useStore = defineStore('collection', {
  state: () => ({
    films: [],
  }),

  actions: {
    getFilms() {
      console.log("Fetching films from database")
      fetch(API_BASE_URL + '/films/')
        .then(response => response.json())
        .then(data => (this.films = data))
        .catch((error) => console.log(error))
    },
    async refreshImdb(slug) {
      console.log(`Searching IMDB for ${slug}`)
      try {
        const response = await fetch(`${API_BASE_URL}/films/${slug}/search`)
        const data = await response.json()
        return data
      } catch (error) {
        console.log(error)
      }
    },
    async refreshFilmMetadata(slug, imdb_id) {
      console.log(`Refreshing ${slug} metadata with IMDB ID ${imdb_id}`)
      // fetch(`${API_BASE_URL}/films/${slug}/refresh?imdb_id=${imdb_id}`)
      //   .then(response => response.json())
      //   .then(data => {
      //     console.log(data)
      //     this.films.map((film) => {
      //       return film
      //     })
      //   })
      //   .catch((error) => console.log(error))
    }
  },

  getters: {
    getFilteredFilms: (state) => {
      return (titleFilter) => {
        if (!titleFilter)
          return state.films

        titleFilter = titleFilter.toLowerCase()

        console.log('filter titles by =>', titleFilter)

        return state.films.filter((film) => {
          return ((
            film.display_title ? film.display_title
              .toLowerCase().startsWith(titleFilter) : false) ||
                film.title.toLowerCase().startsWith(titleFilter))
        })
      }
    }
  }
})

import { defineStore } from 'pinia'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export const useFilmsStore = defineStore('films', {
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

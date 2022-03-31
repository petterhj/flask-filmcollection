<script setup>
import { ref } from 'vue'
import { useStore } from './store'
import RefreshMetadataModal from './components/RefreshMetadataModal.vue'

const store = useStore()
store.getFilms()

const titleFilter = ref('')
const selectedFilm = ref(null)

// function refreshMetadata(film) {
//   // store.refreshFilmMetadata(film.lb_slug, 'tt0841044')
//   this.selectedFilm = film  
// }

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
</script>

<template>
  <nav class="navbar bg-base-300">
    <div class="flex-1">
      <a class="btn btn-ghost normal-case text-xl">
        FC
      </a>
    </div>
    <div class="flex-none">
      <button class="btn btn-square btn-ghost">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z"></path></svg>
      </button>
    </div>
  </nav>

  <section class="p-8 pt-3">
    <input
      type="text"
      class="input input-lg input-bordered w-full mb-6"
      v-model="titleFilter"
    >

    <div
      v-for="film in store.getFilteredFilms(titleFilter)"
      :key="film.slug"
      class="flex mb-3 p-4 bg-base-100 rounded-lg shadow-md h-26"
    >
      <div class="flex-none w-12 mr-4">
        <img
          class="rounded h-full"
          v-if="film.has_poster"
          :src="`${API_BASE_URL}/films/${film.lb_slug}/poster.jpg`"
          :alt="film.title + ' poster'"
        />
      </div>
      <div class="flex-1">
        <h1 class="font-bold text-md">{{ film.display_title || film.title }}</h1>
        <h2 class="font-semibold text-neutral-focus text-sm">{{film.title}}</h2>
        <button @click="selectedFilm = film">Refresh metadata</button>
      </div>
    </div>
  </section>

  <refresh-metadata-modal
    :film="selectedFilm"
    @close="selectedFilm = null"
  />
</template>

<script setup>
import { ref, watch } from 'vue'
import { DotsHorizontalIcon } from '@heroicons/vue/solid'

import { useFilmsStore } from './store/films'
import { useFilmStore } from './store/film'
import FilmDetailModal from './components/FilmDetailModal.vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const store = useFilmsStore()
const filmStore = useFilmStore()

const titleFilter = ref('')
const filmModalOpen = ref(false)

store.getFilms()

// filmStore.$subscribe((mutation, state) => {
//   // console.log(mutation)
//   console.log(state)
// })

function showFilmModal(film) {
  filmStore.film = film
  filmModalOpen.value = true
}
function closeFilmModal() {
  filmStore.$reset()
  filmModalOpen.value = false
}

// watch(() => filmStore.searchResults, (results) => {
  
// })

function getMediaImage(mediaType) {
  return new URL(`./assets/${mediaType}.png`, import.meta.url).href
}

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
        <dots-horizontal-icon class="inline-block w-5 h-5 stroke-current" />
      </button>
    </div>
  </nav>

  <section class="p-8 pt-3">
    <input
      type="text"
      class="input input-lg input-bordered w-full mb-6"
      v-model="titleFilter"
    />

    <div
      v-for="film in store.getFilteredFilms(titleFilter)"
      :key="film.slug"
      class="flex mb-3 p-4 bg-base-100 border-4 rounded-lg shadow-md cursor-pointer"
      :class="[
        filmStore.film?.lb_slug === film.lb_slug ? 'border-amber-600' : 'border-base-100'
      ]"
      @click="showFilmModal(film)"
    >
      <div class="flex-none w-12 mr-4">
        <img
          class="rounded w-12 h-16"
          v-if="film.has_poster"
          :src="`${API_BASE_URL}/films/${film.lb_slug}/poster.jpg`"
          :alt="film.title + ' poster'"
        />
      </div>
      <div class="flex-1">
        <h1 class="font-bold text-md">
          {{ film.display_title || film.title }} | I:{{film.imdb_id}}
        </h1>
        <h2 class="font-semibold text-neutral-focus text-sm">
          {{film.title}}
        </h2>
      </div>
      <div class="flex-none">
        <img
          v-for="media in film.media"
          :key="media.id"
          :src="getMediaImage(media.media_type)"
          class="w-6 h-6 mt-2"
        />
      </div>
    </div>
  </section>
  
  <film-detail-modal
    :open="filmModalOpen"
    @close="closeFilmModal"
  />
</template>

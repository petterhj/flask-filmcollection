<script setup>
import { computed, reactive, ref } from 'vue'
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

function showFilmModal(film) {
  filmStore.film = film
  filmModalOpen.value = true
}
function closeFilmModal() {
  filmStore.$reset()
  filmModalOpen.value = false
}

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
    <!-- Filter -->
    <input
      type="text"
      class="input input-lg input-bordered w-full mb-6"
      v-model="titleFilter"
    />

    <!-- Films -->
    <div
      v-for="film in store.getFilteredFilms(titleFilter)"
      :key="film.slug"
      class="
        flex gap-6 items-center mb-3 p-4
        bg-base-100 border-4 rounded-lg
        shadow-md cursor-pointer
      "
      :class="[
        filmStore.film?.lb_slug === film.lb_slug ? 'border-amber-600' : 'border-base-100',
        film.media.length === 0 ? 'opacity-50' : ''
      ]"
      @click="showFilmModal(film)"
    >
      <div class="flex-none w-12">
        <img
          class="rounded w-12 h-16"
          v-if="film.has_poster"
          :src="`${API_BASE_URL}/films/${film.lb_slug}/poster.jpg`"
          :alt="film.title + ' poster'"
        />
      </div>
      <div class="flex-1">
        <h1 class="font-bold text-lg">
          {{ film.display_title || film.title }}
        </h1>
        <h2 class="font-semibold text-neutral-focus text-sm">
          {{film.title}}
        </h2>
      </div>
      <div class="flex-none">
        <div class="stack">
          <img
            v-for="media in film.media"
            :key="media.id"
            :src="getMediaImage(media.media_type)"
            class="w-6 h-6 mt-2"
          />
        </div>
      </div>
    </div>
  </section>
  
  <film-detail-modal
    :open="filmModalOpen"
    @close="closeFilmModal"
  />
</template>

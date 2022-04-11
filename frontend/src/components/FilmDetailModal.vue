<script setup>
import { computed, ref, reactive, watch, toRef } from 'vue'
import { RefreshIcon } from '@heroicons/vue/solid'
// import VueBarcode from '@chenfengyuan/vue-barcode'

import { useFilmStore } from '../store/film'
import FilmMetadataForm from './FilmMetadataForm.vue'
import Barcode  from './Barcode.vue'

const store = useFilmStore()

defineProps({
  open: Boolean
})

const showEditForm = ref(false)

const emit = defineEmits(['close'])

function updateMetadata() {
  if (showEditForm.value === true) {
    showEditForm.value = false
    return
  }
  showEditForm.value = true
  store.metadataPatch = JSON.parse(JSON.stringify(store.patchable))
  if (store.searchResults.length === 0)
    store.searchMetadata()
}
function close() {
  showEditForm.value = false
  emit('close')
}
function getMediaImage(mediaType) {
  return new URL(`../assets/${mediaType}.png`, import.meta.url).href
}
function getMediaStyle(mediaType) {
  switch (mediaType) {
    case 'br':
      return 'bg-blue-900 text-blue-100'
    case 'dvd':
      return 'bg-zinc-200 text-zinc-900'
    case 'uhd':
      return 'bg-zinc-900 text-zinc-200'
    default:
      return 'border-neutral'
  }
}
</script>

<template>
  <input  
    type="checkbox"
    class="modal-toggle"
    :checked="open"
  >
  <div
    class="modal modal-bottom sm:modal-middle cursor-pointer"
    @click.self="close"
    v-if="store.film"
  >
    <label class="modal-box relative" for="modal">
      <!-- Header -->
      <div class="flex">
        <div class="flex-1 font-bold">
          <h3 class="flex-1 text-lg">
            <span class="text-orange-400">{{store.film.display_title || store.film.title}}</span> ({{store.film.year}})
          </h3>
          <span
            v-if="store.film.display_title"
            class="text-neutral-focus text-sm"
          >{{store.film.title}}</span>
        </div>
        <refresh-icon
          class="flex-none h-5 mt-1 text-neutral-focus hover:text-neutral-content cursor-pointer"
          title="Refresh metadata"
          @click="updateMetadata"
        />
      </div>

      <!-- Metadata -->
      <template v-if="!showEditForm">
        <p v-if="store.film.summary" class="text-xs leading-5 mt-3 mb-4">
          {{store.film.summary}}
        </p>
        <div class="flex gap-2">
          <div
            title="Genres"
            class="badge badge-md"
            v-if="store.film.genres">
            {{store.film.genres}}
          </div>
          <div
            title="Runtime"
            class="badge badge-md"
            v-if="store.film.runtime">
            {{store.film.runtime}} min
          </div>
          <div  
            title="IMDb rating"
            class="badge badge-md badge-warning"
            v-if="store.film.imdb_rating">
            {{store.film.imdb_rating}}
          </div>
          <div
            title="Meta score"
            class="badge badge-md badge-info"
            v-if="store.film.meta_score">
            {{store.film.meta_score}}
          </div>
        </div>
      </template>
      
      <div class="bg-base-300 mb-4 p-4 rounded-lg text-sm mt-4"
        v-else
      >
        <film-metadata-form @done="showEditForm = false" />
      </div>

      <!-- Media -->
      <div class="flex flex-col gap-3 mt-6">
        <div
          v-for="media in store.film.media"
          :key="media.id"
          class="
            flex gap-6 items-center p-4
            bg-neutral rounded-lg
            shadow-md cursor-pointer
          "
          :class="[getMediaStyle(media.media_type)]"
        >
          <div class="flex-1">
            <div class="stat p-2">
              <div class="stat-value uppercase text-lg">{{media.media_type}}</div>
              <div class="stat-desc text-xs">{{media.added_at}}</div>
            </div>
            <div class="alert alert-error text-xs p-1">
              <span>Not in Letterboxd list!</span>
            </div>
          </div>
          <div class="flex-1 h-full">
            <barcode
              class="rounded border-4 border-base-100 p-1 bg-[#FFFFFF] h-26"
              v-if="media.barcode"
              :value="media.barcode"
              line-color="#0C1322"
              background-color="#FFFFFF"
            />
            <div
              v-else
              class="rounded border-4 border-base-100 p-1 bg-info-content h-full"
            >
              asdasd
            </div>
          </div>
        </div>
      </div>
        
      <!--div class="modal-action">
        <button
          class="btn btn-outline"
          @click="$emit('close')"
        >Close</button>
        <button
          class="btn btn-success"
          @click="store.refreshMetadata(selectedImdbId); $emit('close')"
          :disabled="store.isSearching || store.searchResults.length === 0"
        >Refresh</button>
      </div-->
    </label>
  </div>
</template>

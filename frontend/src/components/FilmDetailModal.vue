<script setup>
import { computed, ref, reactive, watch, toRef } from 'vue'
import { RefreshIcon } from '@heroicons/vue/solid'

import { useFilmStore } from '../store/film'
import FilmMetadataForm from './FilmMetadataForm.vue'

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
      <div class="flex mb-4">
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
        <p v-if="store.film.summary" class="text-xs leading-5 mb-4">
          {{store.film.summary}}
        </p>
      </template>
      
      <div class="bg-base-300 mb-4 p-4 rounded-lg text-sm"
        v-else
      >
        <film-metadata-form @done="showEditForm = false" />
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

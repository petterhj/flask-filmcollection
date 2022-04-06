<script setup>
import { ref, watch, toRef } from 'vue'
import { RefreshIcon } from '@heroicons/vue/solid'

import { useFilmStore } from '../store/film'


const props = defineProps({
  open: Boolean
})

const store = useFilmStore()
const showEditForm = ref(false)
// const searchResults = toRef(store.searchResults)

// console.log(store.searchResults)

const emit = defineEmits(['close'])

// watch(props.open, (modalOpened) => {
//   if (modalOpened && store.film)
//     store.searchMetadata()
// })
// watch(store.searchResults, (results) => {
//   console.log(results)
// })
// function showFilmModal(film) {
//   filmStore.film = film
//   filmModalOpen.value = true
// }

function searchMetadata() {
  if (showEditForm.value === true) {
    showEditForm.value = false
    return
  }
  showEditForm.value = true
  store.filmPatch.title = store.film.title
  store.filmPatch.display_title = store.film.display_title
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
    <label class="modal-box relative">
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
          @click="searchMetadata"
        />
      </div>
      <!-- Metadata -->
      <template v-if="!showEditForm">
        <p v-if="store.film.summary" class="text-xs leading-5 mb-4">
          {{store.film.summary}}
        </p>
      </template>
      
      <div
        class="bg-base-300 mb-4 p-4 rounded-lg text-sm"
        v-if="showEditForm"
      >
        <div class="form-control mb-2">
          <label class="label pt-0 pl-0">
            <span class="label-text text-neutral-focus">Source</span>
          </label>

          <progress class="progress" v-if="store.isSearching"></progress>
          <template v-else>
            <div  
              v-if="store.searchResults.length === 0"
              class="alert alert-warning shadow-lg"
            >
              <div>
                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                <span>Nothing found matching query!</span>
              </div>
            </div>
            <label
              class="flex items-center mb-4 last:mb-0"
              v-for="(result, index) in store.searchResults"
              :key="result.imdb_id"
            >
              <input
                type="radio"
                name="selectedResult"
                class="radio radio-xs radio-secondary flex-0 mr-3"
                :value="result.imdb_id"
                v-model="store.filmPatch.imdb_id"
              >
              <span class="flex-1">
                {{result.title}} ({{result.year}}) <a 
                class="text-amber-300 hover:text-amber-200 text-xs"
                :href="`https://imdb.com/title/${result.imdb_id}`"
                target="_blank"
                tabindex="-1">IMDb</a>
              </span>
            </label>
          </template>
        </div>

        <div class="form-control mb-2">
          <label class="label pl-0">
            <span class="label-text text-neutral-focus">Title</span>
          </label>
          <input
            type="text"
            class="input input-bordered w-full"
            v-model="store.filmPatch.title"
          />
        </div>
        <div class="form-control mb-6">
          <label class="label pl-0">
            <span class="label-text text-neutral-focus">Display title</span>
          </label>
          <input
            type="text"
            class="input input-bordered w-full"
            v-model="store.filmPatch.display_title"
          />
        </div>
        <div class="flex mt-4">
          <button class="btn btn-outline flex-none mr-2" @click="showEditForm = false">Cancel</button>
          <button class="btn btn-success flex-1" :disabled="!store.isPatched">Save</button>
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

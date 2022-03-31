<script setup>
import { ref, toRef, watch } from 'vue'
import { useStore } from '../store'

const props = defineProps({
  film: Object
})

const store = useStore()
const film = toRef(props, 'film')
const isSearching = ref(false)
const searchResults = ref(null)
const selectedImdbId = ref(null)

defineEmits(['close'])

watch(film, (filmToSearch) => {
  searchResults.value = []
  if (!filmToSearch)
    return
  isSearching.value = true
  store.refreshImdb(filmToSearch.lb_slug)
    .then(results => {
      searchResults.value = results
    })
    .catch((error) => console.error(error))
    .finally(() => isSearching.value = false)

})
</script>

<template>
  <input  
    type="checkbox"
    class="modal-toggle"
    :checked="film ? true : false"
  >
  <div
    class="modal modal-bottom sm:modal-middle cursor-pointer"
    @click.self="$emit('close')"
    v-if="film"
  >
    <label class="modal-box relative" for="">
      <h3 class="text-lg font-bold mb-4">
        Refresh metadata for <span class="text-orange-400">{{film.display_title || film.title}}</span>
      </h3>
      <template v-if="!isSearching">
        <div  
          v-if="searchResults.length === 0"
          class="alert alert-warning shadow-lg"
        >
          <div>
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
            <span>Nothing found matching query!</span>
          </div>
        </div>
        <div
          class="flex"
          v-for="(result, index) in searchResults"
          :key="result.imdb_id"
        >
          <div class="flex-none p-2">
            <input
              type="radio"
              name="selectedResult"
              class="radio radio-secondary"
              :value="result.imdb_id"
              :checked="index === 0"
              v-model="selectedImdbId"
            >
          </div>
          <div class="flex-1 p-2">
            {{result.title}} ({{result.year}})
          </div>
        </div>
      </template>
      <p v-else>Searching...</p>
        
      <div class="modal-action">
        <button
          class="btn btn-outline"
          @click="this.$emit('close')"
        >Abort</button>
        <button
          class="btn btn-success"
          @click="store.refreshFilmMetadata(film.lb_slug, selectedImdbId); $emit('close')"
          :disabled="isSearching || searchResults.length === 0"
        >Ya!y!</button>
      </div>
    </label>
  </div>
</template>

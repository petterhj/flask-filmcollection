<script setup>
import { ref, watch, toRef } from 'vue'
import { useFilmStore } from '../store/film'

const props = defineProps({
  open: Boolean
})

const store = useFilmStore()
const selectedImdbId = ref(null)
// const searchResults = toRef(store.searchResults)

// console.log(store.searchResults)

defineEmits(['close'])

// watch(props.open, (modalOpened) => {
//   if (modalOpened && store.film)
//     store.searchMetadata()
// })
// watch(store.searchResults, (results) => {
//   console.log(results)
// })
</script>

<template>
  <input  
    type="checkbox"
    class="modal-toggle"
    :checked="open"
  >
  <div
    class="modal modal-bottom sm:modal-middle cursor-pointer"
    @click.self="$emit('close')"
    v-if="store.film"
  >
    <label class="modal-box relative" for="">
      <h3 class="text-lg font-bold mb-4">
        <span class="text-orange-400">{{store.film.display_title || store.film.title}}</span> ({{store.film.year}})
      </h3>
      <template v-if="!store.isSearching">
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
          class="flex mb-4"
          v-for="(result, index) in store.searchResults"
          :key="result.imdb_id"
        >
          <input
            type="radio"
            name="selectedResult"
            class="radio radio-secondary flex-0 mr-2"
            :value="result.imdb_id"
            :checked="index === 0"
            v-model="selectedImdbId"
          >
          <span class="flex-1">
            {{result.title}} ({{result.year}}) <a 
            class="text-amber-300 hover:text-amber-200 text-xs"
            :href="`https://imdb.com/title/${result.imdb_id}`"
            target="_blank">IMDb</a>
          </span>
        </label>
      </template>
      <progress class="progress" v-else></progress>

      <hr>
      <div class="form-control">
        <label class="label">
          <span class="label-text">Title</span>
        </label>
        <input type="text" class="input input-bordered w-full" :value="store.film.title">
      </div>
      <div class="form-control">
        <label class="label">
          <span class="label-text">Display title</span>
        </label>
        <input type="text" class="input input-bordered w-full" :value="store.film.display_title">
      </div>
      <hr>
        
      <div class="modal-action">
        <button
          class="btn btn-outline"
          @click="$emit('close')"
        >Close</button>
        <button
          class="btn btn-success"
          @click="store.refreshMetadata(selectedImdbId); $emit('close')"
          :disabled="store.isSearching || store.searchResults.length === 0"
        >Refresh</button>
      </div>
    </label>
  </div>
</template>

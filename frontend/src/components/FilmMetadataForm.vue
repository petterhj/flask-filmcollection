<script setup>
import { computed, ref, reactive, watch, toRef } from 'vue'
import { 
  ChevronDoubleDownIcon,
  ReplyIcon,
  SwitchVerticalIcon,
} from '@heroicons/vue/solid'

import { useFilmStore } from '../store/film'

const store = useFilmStore()

const emit = defineEmits(['done'])

function swapMetadataTitles() {
  const currentTitle = store.metadataPatch.title
  store.metadataPatch.title = store.metadataPatch.display_title
  store.metadataPatch.display_title = currentTitle
}
function saveMetadata() {
  emit('done')
}

</script>

<template>
  <!-- Metadata source -->
  <div class="form-control mb-2">
    <label class="label pt-0 pl-0">
      <span class="label-text text-neutral-focus uppercase text-xs">Source</span>
    </label>
    <progress class="progress" v-if="store.isSearching" />
    <template v-else>
      <!-- Alert: No results-->
      <div  
        class="alert alert-warning shadow-lg"
        v-if="store.searchResults.length === 0"
      >
        <div>
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          <span>Nothin found!</span>
        </div>
      </div>

      <!-- Search results -->
      <label
        class="flex items-center mb-4 last:mb-0 text-sm"
        v-for="result in store.searchResults"
        :key="result.imdb_id"
      >
        <input
          type="radio"
          name="metadataSource"
          class="radio radio-xs radio-primary flex-0 mr-3"
          :value="result.imdb_id"
          v-model="store.metadataPatch.imdb_id"
        />

        <span class="flex-1">
          {{result.title}}
          <span class="text-xs text-neutral-focus ml-1">
            {{result.year}} <a 
              class="text-amber-300 hover:text-amber-200 text-xs ml-1"
              :href="`https://imdb.com/title/${result.imdb_id}`"
              target="_blank"
              :title="result.imdb_id"
              tabindex="-1">IMDb</a>
          </span>
        </span>
      </label>

    </template>
  </div>

  <!-- Titles -->
  <div class="flex items-center">
    <div class="flex-1">
      <!-- Title -->
      <div class="form-control mb-2">
        <label class="label pl-0">
          <span class="label-text text-neutral-focus uppercase text-xs">Title</span>
        </label>
        <div :class="{'input-group': ((
          store.selectedMetadataSource && (
            store.selectedMetadataSource.title !== store.metadataPatch.title
          )) || (store.film.title !== store.metadataPatch.title))}">
          <input
            type="text"
            class="input input-bordered w-full "
            v-model="store.metadataPatch.title"
          />
          <button
            class="btn btn-square btn-warning"
            v-if="store.film.title !== store.metadataPatch.title"
            @click="store.metadataPatch.title = store.film.title"
          >
            <reply-icon
              class="h-5 text-neutral-focus"
              title="Revert to current title"
            />
          </button>
          <button
            class="btn btn-square btn-info"
            v-if="(store.selectedMetadataSource && (
              store.selectedMetadataSource.title !== store.metadataPatch.title
            ))"
            @click="store.metadataPatch.title = store.selectedMetadataSource.title"
          >
            <chevron-double-down-icon
              class="h-5 text-neutral-focus"
              title="Update title from source"
            />
          </button>
        </div>
      </div>

      <!-- Display title -->
      <div class="form-control mb-2">
        <label class="label pl-0">
          <span class="label-text text-neutral-focus uppercase text-xs">Display title</span>
        </label>
        <div :class="{'input-group': ((
          store.selectedMetadataSource && (
            store.selectedMetadataSource.title !== store.metadataPatch.display_title
          )) || (store.film.display_title !== store.metadataPatch.display_title))}">
          <input
            type="text"
            class="input input-bordered w-full "
            v-model="store.metadataPatch.display_title"
          />
          <button
            class="btn btn-square btn-warning"
            v-if="store.film.display_title !== store.metadataPatch.display_title"
            @click="store.metadataPatch.display_title = store.film.display_title"
          >
            <reply-icon
              class="h-5 text-neutral-focus"
              title="Revert to current title"
            />
          </button>
          <button
            class="btn btn-square btn-info"
            v-if="(store.selectedMetadataSource && (
              store.selectedMetadataSource.title !== store.metadataPatch.display_title
            ))"
            @click="store.metadataPatch.display_title = store.selectedMetadataSource.title"
          >
            <chevron-double-down-icon
              class="h-5 text-neutral-focus"
              title="Update title from source"
            />
          </button>
        </div>
      </div>
    </div>
    <div class="flex-none pl-4">
      <button
        class="mt-6 btn btn-sm btn-circle btn-secondary"
        @click="swapMetadataTitles"
      >
        <switch-vertical-icon
          class="h-5 text-neutral-focus"
          title="Swap titles"
        />
      </button>
    </div>
  </div>

  <div class="flex mt-6">
    <button
      class="btn btn-outline flex-none mr-2"
      @click="$emit('done')">Cancel</button>
    <button
      class="btn btn-success flex-1"
      @click="saveMetadata"
      :disabled="!store.hasPatchedMetadata">Save</button>
  </div>
</template>
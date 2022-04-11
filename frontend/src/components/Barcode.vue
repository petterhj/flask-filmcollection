<script setup>
import { onMounted, onUpdated } from 'vue'
import JsBarcode from "jsbarcode"

const props = defineProps({
  value: Number,
  lineColor: String,
  backgroundColor: String,
})

onMounted(() => {
  JsBarcode('.barcode', props.value, {
    lineColor: props.lineColor,
    background: props.backgroundColor,
  })
})
</script>

<template>
  <div class="barcode-wrapper">
    <svg class="barcode" />
  </div>
</template>

<style scoped>
  .barcode-wrapper {
    overflow: hidden;
  }
  svg.barcode {
    height: 100% !important;
    width: 100% !important;
  }
</style>

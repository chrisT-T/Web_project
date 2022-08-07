<template>
  <div ref="container" class="d-flex" style="min-width: 200px; position:relative">
    <div style="width: 100%; height: 100%">
      <slot>default message</slot>
    </div>
    <div class="resize" ></div>
  </div>
</template>

<script lang="ts">

import { Vue, Options } from 'vue-class-component'

export default class DragItem extends Vue {
}
</script>

<style scoped>
.resize {
  position: absolute;
  top: 0;
  right: 0;
  width: 4px;
  height: 100%;
  cursor: col-resize;
  background-color: #bbbbbb;
  z-index: 999;
}
</style>

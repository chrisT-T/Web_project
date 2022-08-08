<template>
  <div>
    <h1>Drag</h1>
    <drag-box style="width: 100%; height: 100%">
      <drag-item>item1</drag-item>
      <drag-item>item2</drag-item>
    </drag-box>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component'
import DragBox from '@/components/DragBox.vue'
import DragItem from '@/components/DragItem.vue'
@Options({
  components: {
    DragBox,
    DragItem
  }
})
export default class DragView extends Vue {}
</script>

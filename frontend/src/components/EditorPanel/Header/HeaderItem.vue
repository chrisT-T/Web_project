<template>
    <div :class="focus ? 'editor-header-item focus' : 'editor-header-item'">
      <p class="editor-header-item-title" @click="emit('toFocus')">
        {{ title }}
      </p>
      <div class="editor-header-item-operation" @click="emit('close')">
        <div class="editor-header-item-close">
        </div>
      </div>
    </div>
</template>

<script lang="ts" setup>
import { ref, watch, defineProps, defineEmits } from 'vue'

const props = defineProps({
  title: String,
  focus: Boolean
})

const operatorSize = ref('15px')

// on focus, set by parent node
watch(() => props.focus, (newFocus) => {
  if (newFocus) {
    console.log('focus')
  } else {
    console.log('stop focus')
  }
})

const emit = defineEmits(['toFocus', 'close'])

</script>

<style scoped>
.editor-header-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #4D4D4D;
  width: min-content;
  min-width: 50px;
  padding: 5px 5px;
  color: #dddddd;
  user-select: none;
}

.focus {
  background-color: #2D2D2D;
}

p {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  text-align: left;
}
.editor-header-item-close {
    position: relative;
    border-radius: v-bind(operatorSize);
    width: v-bind(operatorSize);
    height: v-bind(operatorSize);
    margin: 2px;
}

.editor-header-item-close:hover {
    position: relative;
    width: v-bind(operatorSize);
    height: v-bind(operatorSize);
    background-color: #aaaaaa;
    border-radius: 3px;
}

.editor-header-item-close::before,
.editor-header-item-close::after {
    position: absolute;
    content: ' ';
    background-color: #888888;
    width: 1px;
    height: v-bind(operatorSize);
}

.editor-header-item-close::before {
    transform: rotate(45deg);
}

.editor-header-item-close::after {
    transform: rotate(-45deg);
}
</style>

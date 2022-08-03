<template>
    <div class="editor-header-bar">
      <div class="editor-header-bar-item" v-for="(item, index) in titles" v-bind:key="item">
        <HeaderItem :title="item" :focus="focusList[index]" :modified="modifiedList[index]"  @to-focus="emit('focusToItem', index)" @close="emit('closeItem', index)" draggable="true"></HeaderItem>
        <div class="editor-header-bar-item-separation"></div>
      </div>
    </div>
</template>

<script lang="ts" setup>
import HeaderItem from './HeaderItem.vue'
import { ref, defineEmits, defineExpose, defineProps } from 'vue'

const props = defineProps<{
  titles: Array<string>,
}>()

const focusList = ref<Array<boolean>>(props.titles.map(() => false))
const modifiedList = ref<Array<boolean>>(props.titles.map(() => false))

// eslint-disable-next-line func-call-spacing
const emit = defineEmits<{
  (e: 'focusToItem', index: number): void
  (e: 'closeItem', index: number): void
}> ()

function changeFocus (index: number) {
  console.log('change focus' + index)
  focusList.value = focusList.value.map((item, i) => i === index)
}

function modified (index: number) {
  console.log('change modified' + index)
  modifiedList.value[index] = true
}

function saved (index: number) {
  console.log('change saved' + index)
  modifiedList.value[index] = false
}

function getCurrentFocus () {
  return focusList.value.indexOf(true)
}

function saveCurrent () {
  const index = getCurrentFocus()
  saved(index)
}

function modifyCurrent () {
  const index = getCurrentFocus()
  modified(index)
}

defineExpose({
  changeFocus,
  saveCurrent,
  modifyCurrent
})

</script>

<style scoped>
.editor-header-bar {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  background-color: #4D4D4D;
  width: 100%;
  height: 30px;
  color: #dddddd;
}
.editor-header-bar-item {
  display: flex;
  align-items: center;
}
.editor-header-bar-item-separation {
  width: 1px;
  height: 30px;
  background-color: #1E1E1E;
}
</style>

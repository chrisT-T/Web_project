<template>
    <div class="editor-header-bar">
      <div class="editor-header-bar-item" v-for="(item, index) in items" v-bind:key="item">
        <HeaderItem :title="item" :focus="focusList[index]"  @to-focus="focusToItem(item)" @close="closeItem(item)"></HeaderItem>
        <div class="editor-header-bar-item-separation"></div>
      </div>
    </div>
</template>

<script lang="ts" setup>
import HeaderItem from './HeaderItem.vue'
import { ref, defineEmits } from 'vue'

const items = ref<Array<string>>(['aaaaaaaaaaaaaaaaaa', 'b', 'c'])

const focusList = ref<Array<boolean>>(items.value.map(() => false))

function focusToItem (item: string) {
  const index = items.value.indexOf(item)
  focusList.value = focusList.value.map(() => false)
  focusList.value[index] = true
}

function closeItem (item: string) {
  const index = items.value.indexOf(item)
  items.value.splice(index, 1)
  focusList.value.splice(index, 1)
}

const emit = defineEmits(['changeFocus:item'])
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

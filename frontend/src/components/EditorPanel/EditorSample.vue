<template>
  <div class="home">
    <EditorPanel ref="myEditorPanel" @save-file="displaySaveFile"></EditorPanel>
  </div>
  <div style="height: 200px;"></div>
  <button @click="addFile">Add Random File</button>
  <p id="save-info"></p>
  <button @click="showBreakpoint">Get Break Points</button>
  <p>{{ breakPointInforamtion }}</p>
    <div class="form">
      <label for="path"> File Path: </label>
      <input type="text" v-model="filepath" required>
    </div>
    <div class="form-example">
      <label for="line"> Line Number: </label>
      <input type="number" v-model="lineNumber" required>
    </div>
    <div class="form-example">
      <button @click="focus"> Add </button>
      <button @click="clearFocus"> Clear </button>
    </div>
</template>

<script lang="ts" setup>
import EditorPanel from '@/components/EditorPanel/EditorPanel.vue'
import { ref, shallowRef } from 'vue'

const filepath = ref<string>('')
const lineNumber = ref<number>(0)

const myEditorPanel = shallowRef<InstanceType<typeof EditorPanel> | null>(null)
const breakPointInforamtion = ref<Map<string, Array<number>>>(new Map())

function addFile () {
  const path = `/Users/jerry/Desktop/${Math.floor(Math.random() * 1e9).toString()}.py`
  // get a random english string
  const value = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
  console.log(path, value)
  myEditorPanel.value?.addFile(path, value)
}

function displaySaveFile (path: string, value: string) {
  let innerhtml = document.getElementById('save-info')?.innerHTML as string
  innerhtml += `Save File: ${path} with value: ${value}<br/>`
  const element = document.getElementById('save-info') as HTMLElement
  element.innerHTML = innerhtml
}

function focus () {
  if (filepath.value === '') {
    alert('Please input file path')
    return
  }
  myEditorPanel.value?.focusLine(filepath.value, lineNumber.value)
}

function clearFocus () {
  myEditorPanel.value?.clearFocusLine()
}

function showBreakpoint () {
  console.log(myEditorPanel.value?.getBreakpoints())
  breakPointInforamtion.value = myEditorPanel.value?.getBreakpoints() as Map<string, Array<number>>
}
</script>

<style scoped>
.home {
  height: 500px;
}
</style>

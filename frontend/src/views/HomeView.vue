<template>
  <div class="home">
    <!-- <MonacoEditor :editor-option="option" ref="myeditor"> </MonacoEditor> -->
    <EditorPanel ref="myEditorPanel"></EditorPanel>
  </div>
  <button @click="addFile">Add Random File</button>

</template>

<script lang="ts" setup>
import EditorPanel from '@/components/EditorPanel/EditorPanel.vue'
import { shallowRef } from 'vue'

const myEditorPanel = shallowRef<InstanceType<typeof EditorPanel> | null>(null)

function addFile () {
  const path = `/Users/jerry/Desktop/${Math.floor(Math.random() * 1e9).toString()}.txt`
  // get a random english string
  const value = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)

  console.log(path, value)

  myEditorPanel.value?.addFile(path, value)
}
</script>

<style scoped>
.home {
  height: 500px;
}
</style>

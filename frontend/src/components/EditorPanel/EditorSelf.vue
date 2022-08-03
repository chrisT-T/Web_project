<template>
  <!-- 这个是单个的“编辑器”，包括上面的标签页栏 和导航栏 (如果有) -->
  <div>
    <EditorHeader ref="editorHeader" :titles="titles" @focus-to-item="changeFocus"></EditorHeader>
    <MonacoEditor ref="editorItself" :editor-option="monacoEditorOption" @modified="editorModified" @saved="editorSaved"></MonacoEditor>
  </div>
</template>

<script lang="ts" setup>
import EditorHeader from './Header/EditorHeader.vue'
import MonacoEditor from './MonacoEditor/MonacoEditor.vue'
import { onMounted, shallowRef } from 'vue'

const monacoEditorOption = {
  theme: 'vs-dark',
  glyphMargin: true,
  language: 'python'
}

const titles = ['a', 'b', 'c']
const values = ['aaaaaaaa', 'bbbbbbbb', 'cccccccc']

const editorHeader = shallowRef<InstanceType<typeof EditorHeader> | null>(null)
const editorItself = shallowRef<InstanceType<typeof MonacoEditor> | null>(null)

async function createMonacoModels () {
  values.forEach(value => {
    editorItself.value?.createModel(value, 'python')
  })
}

onMounted(async () => {
  await createMonacoModels()
  editorHeader.value?.changeFocus(0)
  console.log(editorItself.value)
  editorItself.value?.setModel(0)
})

function changeFocus (index : number) {
  console.log(editorHeader.value)
  editorHeader.value?.changeFocus(index)
  editorItself.value?.setModel(index)
}

function editorModified () {
  editorHeader.value?.modifyCurrent()
}
function editorSaved () {
  editorHeader.value?.saveCurrent()
}
</script>

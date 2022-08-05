<template>
  <!-- 这个是单个的“编辑器”，包括上面的标签页栏 和导航栏 (如果有) -->
  <div class="editor-base-container">
    <!-- header -->
    <div class="editor-header-bar">
      <draggable v-model="thisFileItems" item-key="path" group="editor-header-item" direction="vertical" :prevent-on-filter="true"
        style="display: flex; flex-direction: row; width: 100%;">
        <template #item="{ element, index }">
          <div style="display: flex;">
            <HeaderItem :title="element.title" :focus="element.focus" :modified="getModified(index)"
              @to-focus="changeFocus(index)" @close="close(index)"></HeaderItem>
            <div class="editor-header-bar-item-separation"></div>
          </div>
        </template>
      </draggable>
    </div>
    <!-- editor -->
    <MonacoEditor ref="editorItself" :editor-option="monacoEditorOption" @modified="modifyCurrent()"
      @saved="saveCurrent()"></MonacoEditor>
  </div>
</template>

<script lang="ts" setup async>
import HeaderItem from './HeaderItem.vue'
import Draggable from 'vuedraggable'
import MonacoEditor from './MonacoEditor/MonacoEditor.vue'
import * as monaco from 'monaco-editor'
import { ref, onMounted, shallowRef, inject, defineProps, onBeforeMount, computed } from 'vue'
import { FileStatus, FileInfo, FileModel } from './EditorPanel.vue'

const fileStatus = inject('fileStatus') as Map<string, FileStatus>
const fileModels = inject('fileModels') as Map<string, FileModel>
const fileItems = inject('fileItems') as Map<number, Array<FileInfo>>

const props = defineProps<{
  id: number,
}>()

const thisFileItems = computed({
  get () {
    return fileItems.get(props.id)
  },
  set (val) {
    if (val !== undefined) {
      fileItems.set(props.id, val)
    }
  }
})

console.log(thisFileItems)

const monacoEditorOption = {
  theme: 'vs-dark',
  glyphMargin: true,
  language: 'python',
  automaticLayout: true,
  bracketPairColorization: true
} as monaco.editor.IStandaloneEditorConstructionOptions

// path to model
// const models = shallowRef<Map<string, monaco.editor.ITextModel>>(new Map<string, monaco.editor.ITextModel>())

// async function init (titles: string[], values: string[]) {
//   // create fileItems
//   for (let i = 0; i < titles.length; i++) {
//     const item = {
//       path: titles[i],
//       title: titles[i],
//       language: 'python',
//       modified: false,
//       focused: false
//     }
//     fileItems.value.push(item)
//   }
//   // create models
//   values.forEach((value, index) => {
//     models.value.set(fileItems.value[index].path, monaco.editor.createModel(value, 'python'))
//   })
// }

const editorItself = shallowRef<InstanceType<typeof MonacoEditor> | null>(null)

onMounted(async () => {
  // await init(testTitles, testValues)
  changeFocus(0)
})

function getFileItems () {
  return fileItems.get(props.id) as Array<FileInfo>
}

function setFileItems (val : Array<FileInfo>) {
  fileItems.set(props.id, val)
}

function getPath (index : number) {
  return getFileItems()[index].path
}

function getModel (index : number) {
  return fileModels.get(getPath(index))?.model
}

function getModified (index : number) {
  return fileStatus.get(getPath(index))?.modified
}

function close (index: number) {
  getModel(index)?.dispose()
  fileStatus.delete(getPath(index))
  fileModels.delete(getPath(index))

  getFileItems().splice(index, 1)
}

function changeFocus (index: number) {
  console.log('change focus' + index)
  const gotFileItems = getFileItems()
  for (let i = 0; i < gotFileItems.length; i++) {
    gotFileItems[i].focus = false
  }
  gotFileItems[index].focus = true
  setFileItems(gotFileItems)
  const model = getModel(index)
  if (model !== undefined) {
    editorItself.value?.setModel(model)
  } else {
    console.log('model is undefined')
  }
}

function modified (index: number) {
  console.log('change modified' + index)
  const file = fileStatus.get(getPath(index)) as FileStatus
  file.modified = true
}

function saved (index: number) {
  console.log('change saved' + index)
  const file = fileStatus.get(getPath(index)) as FileStatus
  file.modified = false
}

function getCurrentFocus () {
  const gotFileItems = getFileItems()
  for (let i = 0; i < gotFileItems.length; i++) {
    if (gotFileItems[i].focus) {
      return i
    }
  }
  console.error('no focus')
  return -1
}

function saveCurrent () {
  const index = getCurrentFocus()
  saved(index)
}

function modifyCurrent () {
  const index = getCurrentFocus()
  modified(index)
}
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

.editor-base-container {
  height: 100%;
  width: 100%;
}
</style>

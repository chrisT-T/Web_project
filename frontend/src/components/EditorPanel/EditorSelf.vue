<template>
  <!-- 这个是单个的“编辑器”，包括上面的标签页栏 和导航栏 (如果有) -->
  <div>
    <!-- header -->
    <div class="editor-header-bar">
      <draggable v-model="fileItems" item-key="path" direction="vertical"
        :group="{ name: 'cards', pull: 'clone', put: false }" :prevent-on-filter="true"
        style="display: flex; flex-direction: row; width: 100%;">
        <template #item="{ element, index }">
          <div style="display: flex;">
            <HeaderItem :title="element.title" :focus="element.focused" :modified="element.modified"
              @to-focus="changeFocus(index)" @close="close(index)"></HeaderItem>
            <div class="editor-header-bar-item-separation"></div>
          </div>
        </template>
      </draggable>
      <!-- <div class="editor-header-bar-item" v-for="(item, index) in fileItems" v-bind:key="item.path">
        <HeaderItem :title="item.title" :focus="item.focused" :modified="item.modified" @to-focus="changeFocus(index)"
          @close="close(index)" draggable="true"></HeaderItem>
        <div class="editor-header-bar-item-separation"></div>
      </div> -->
    </div>
    <!-- <EditorHeader ref="editorHeader" :titles="titles" :paths="titles" @focus-to-item="changeFocus"></EditorHeader> -->
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
import { ref, onMounted, shallowRef } from 'vue'

const monacoEditorOption = {
  theme: 'vs-dark',
  glyphMargin: true,
  language: 'python'
}

interface FileItem {
  path: string,
  title: string,
  // model: monaco.editor.ITextModel,
  language: string,
  modified: boolean,
  focused: boolean
}

const fileItems = ref<Array<FileItem>>([])

const testTitles = ['a', 'b', 'c']
const testValues = ['aaaaaaaa', 'bbbbbbbb', 'cccccccc']

const models = shallowRef<monaco.editor.ITextModel[]>([])

async function init (titles: string[], values: string[]) {
  for (let i = 0; i < titles.length; i++) {
    const item = {
      path: titles[i],
      title: titles[i],
      language: 'python',
      modified: false,
      focused: false
    }
    fileItems.value.push(item)
  }
  models.value = values.map((value) => {
    return monaco.editor.createModel(value, 'python')
  })
}

const editorItself = shallowRef<InstanceType<typeof MonacoEditor> | null>(null)

onMounted(async () => {
  await init(testTitles, testValues)
  changeFocus(0)
})

function close (index: number) {
  // TODO: how to be more natural ?
  models.value[index].dispose()
  models.value.splice(index, 1)
  fileItems.value.splice(index, 1)
}

function changeFocus (index: number) {
  console.log('change focus' + index)
  for (let i = 0; i < fileItems.value.length; i++) {
    fileItems.value[i].focused = false
  }
  fileItems.value[index].focused = true
  if (models.value[index]) {
    editorItself.value?.setModel(models.value[index])
  }
}

function modified (index: number) {
  console.log('change modified' + index)
  fileItems.value[index].modified = true
}

function saved (index: number) {
  console.log('change saved' + index)
  fileItems.value[index].modified = false
}

function getCurrentFocus () {
  for (let i = 0; i < fileItems.value.length; i++) {
    if (fileItems.value[i].focused) {
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
</style>

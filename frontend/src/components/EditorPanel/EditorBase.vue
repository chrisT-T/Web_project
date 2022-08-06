<template>
  <!-- 这个是单个的“编辑器”，包括上面的标签页栏 和导航栏 (如果有) -->
  <div class="editor-base-container">
    <!-- header -->
    <div class="editor-header-bar">
      <draggable v-model="thisFileItems" item-key="path" group="editor-header-item" direction="vertical" :prevent-on-filter="true"
        style="display: flex; flex-direction: row; width: 100%;" @add="addedItem" @remove="removedItem">
        <template #item="{ element, index }">
          <div style="display: flex;">
            <HeaderItem :title="element.path.split('/').pop()" :focus="element.focus" :modified="getModified(index)"
              @to-focus="changeFocus(index)" @close="close(index)"></HeaderItem>
            <div class="editor-header-bar-item-separation"></div>
          </div>
        </template>
      </draggable>
    </div>
    <!-- editor -->
    <div class="editor-content">
      <MonacoEditor ref="editorItself" :editor-option="monacoEditorOption"
        @modified="modifyCurrent"
        @saved="saveCurrent"
        @split-current-view="splitCurrentView"
        @change-cursor-focus="changeCursorFocus">
      </MonacoEditor>
    </div>
  </div>
</template>

<script lang="ts" setup async>
import HeaderItem from './HeaderItem.vue'
import Draggable from 'vuedraggable'
import MonacoEditor from './MonacoEditor/MonacoEditor.vue'
import * as monaco from 'monaco-editor'
import { onMounted, shallowRef, inject, defineProps, defineEmits, watch, computed } from 'vue'
import { FileStatus, FileInfo, FileModel } from './EditorPanel.vue'

const fileStatus = inject('fileStatus') as Map<string, FileStatus>
const fileModels = inject('fileModels') as Map<string, FileModel>
const fileItems = inject('fileItems') as Map<number, Array<FileInfo>>

// eslint-disable-next-line func-call-spacing
const emit = defineEmits<{
  (e : 'deleteEditor') : void,
  (e : 'splitCurrentView', direction: 'horizontal' | 'vertical') : void,
  (e : 'changeCursorFocus') : void,
}>()

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

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function addedItem (e : any) {
  changeFocus(e.newIndex)
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function removedItem (e : any) {
  if (thisFileItems.value?.length === 0) {
    emit('deleteEditor')
  } else {
    if (e.oldIndex === 0) {
      changeFocus(0)
    } else {
      changeFocus(e.oldIndex - 1)
    }
  }
}

const monacoEditorOption = {
  theme: 'vs-dark',
  glyphMargin: true,
  language: 'python',
  automaticLayout: true,
  bracketPairColorization: true,
  model: null
} as monaco.editor.IStandaloneEditorConstructionOptions

const editorItself = shallowRef<InstanceType<typeof MonacoEditor> | null>(null)

onMounted(async () => {
  // await init(testTitles, testValues)
  if (fileItems.get(props.id)?.length) {
    changeFocus(0)
  }
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
  const currentCount = fileStatus.get(getPath(index))?.openCount as number
  console.log(currentCount)
  if (currentCount === 1) {
    fileStatus.delete(getPath(index))
    fileModels.get(getPath(index))?.model.dispose()
    fileModels.delete(getPath(index))
  } else {
    fileStatus.set(getPath(index), {
      modified: getModified(index) as boolean,
      openCount: currentCount - 1
    })
  }
  getFileItems().splice(index, 1)
  if (getFileItems().length === 0) {
    emit('deleteEditor')
  } else {
    if (index === 0) {
      changeFocus(0)
    } else {
      changeFocus(index - 1)
    }
  }
}

function changeFocus (index: number) {
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
    console.error('model is undefined')
  }
}

function modified (index: number) {
  const file = fileStatus.get(getPath(index)) as FileStatus
  file.modified = true
}

function saved (index: number) {
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

function splitCurrentView (direction: 'horizontal' | 'vertical') {
  console.log('split current view')
  emit('splitCurrentView', direction)
}

function changeCursorFocus () {
  emit('changeCursorFocus')
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

.editor-content {
  visibility: v-bind('thisFileItems?.length ? "visible" : "hidden"');
  height: calc(100% - 30px);
}
</style>

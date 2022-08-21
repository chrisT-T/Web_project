<template>
  <!-- 这个是单个的“编辑器”，包括上面的标签页栏 和导航栏 (如果有) -->
  <div class="editor-base-container">
    <!-- header -->
    <div class="editor-header-bar">
      <draggable v-model="fileItems" item-key="path" group="editor-header-item" direction="vertical" :prevent-on-filter="true"
        style="display: flex; flex-direction: row; width: 100%; font-size: 16px" @add="addedItem" @remove="removedItem">
        <template #item="{ element, index }">
          <div style="display: flex;">
            <HeaderItem :title="element.path.split('/').pop()" :focus="element.focus" :modified="getModified(index)"
              @to-focus="changeFocus(index)" @close="close(index)"></HeaderItem>
            <div class="editor-header-bar-item-separation"></div>
          </div>
        </template>
      </draggable>
      <el-button :icon="CaretRight" v-if="Object.keys(fileItems).length > 0" class="debug-button" title="Run in Debug mode" @click="startDebug" circle />
    </div>
    <!-- editor -->
    <div class="editor-content">
      <MonacoEditor ref="editorItself" :editor-option="monacoEditorOption"
        @modified="modifyCurrent"
        @saved="saveCurrent"
        @change-cursor-focus="emit('changeCursorFocus')">
      </MonacoEditor>
    </div>
  </div>
</template>

<script lang="ts" setup async>
import HeaderItem from './HeaderItem.vue'
import Draggable from 'vuedraggable'
import MonacoEditor from './MonacoEditor/MonacoEditor.vue'
import * as monaco from 'monaco-editor'
import { Ref, onMounted, shallowRef, inject, defineEmits, defineExpose } from 'vue'
import { FileStatus, FileInfo, FileModel } from './EditorPanel.vue'
import {
  CaretRight
} from '@element-plus/icons-vue'

const fileStatus = inject('fileStatus') as Ref<Map<string, FileStatus>>
const fileModels = inject('fileModels') as Ref<Map<string, FileModel>>
const fileItems = inject('fileItems') as Ref<Array<FileInfo>>

// eslint-disable-next-line func-call-spacing
const emit = defineEmits<{
  (e : 'deleteEditor') : void,
  (e : 'changeCursorFocus') : void,
  (e : 'saveFile', path :string) : void,
  (e : 'startDebug', path :string) : void,
}>()

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function addedItem (e : any) {
  changeFocus(e.newIndex)
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function removedItem (e : any) {
  if (fileItems.value.length === 0) {
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
  theme: 'vs',
  glyphMargin: true,
  language: 'python',
  automaticLayout: true,
  bracketPairColorization: true,
  model: null
} as monaco.editor.IStandaloneEditorConstructionOptions

const editorItself = shallowRef<InstanceType<typeof MonacoEditor> | null>(null)

onMounted(async () => {
  // await init(testTitles, testValues)
  changeFocus(0)
})

function getFileItems () {
  return fileItems.value as Array<FileInfo>
}

function setFileItems (val : Array<FileInfo>) {
  fileItems.value = val
}

function getPath (index : number) {
  return getFileItems()[index].path
}

function getModel (index : number) {
  return fileModels.value.get(getPath(index))?.model
}

function getModified (index : number) {
  return fileStatus.value.get(getPath(index))?.modified
}

function close (index: number) {
  const currentCount = fileStatus.value.get(getPath(index))?.openCount as number
  console.log(currentCount)
  if (currentCount === 1) {
    fileStatus.value.delete(getPath(index))
    fileModels.value.get(getPath(index))?.model.dispose()
    fileModels.value.delete(getPath(index))
  } else {
    fileStatus.value.set(getPath(index), {
      modified: getModified(index) as boolean,
      openCount: currentCount - 1
    })
  }
  getFileItems().splice(index, 1)
  if (getFileItems().length > 0) {
    if (index === 0) {
      changeFocus(0)
    } else {
      changeFocus(index - 1)
    }
  }
}

function changeFocus (index: number, line? :number) {
  const gotFileItems = getFileItems()
  if (gotFileItems.length === 0) {
    return
  }
  for (let i = 0; i < gotFileItems.length; i++) {
    gotFileItems[i].focus = false
  }
  gotFileItems[index].focus = true
  setFileItems(gotFileItems)
  const model = getModel(index)
  if (model !== undefined) {
    editorItself.value?.setModel(model)
    if (line !== undefined) {
      editorItself.value?.locateToLine(line)
    }
  } else {
    console.error('model is undefined')
  }
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
  const file = fileStatus.value.get(getPath(index)) as FileStatus
  file.modified = false
  emit('saveFile', getPath(index))
}

function modifyCurrent () {
  const index = getCurrentFocus()
  const file = fileStatus.value.get(getPath(index)) as FileStatus
  file.modified = true
}

function startDebug () {
  const index = getCurrentFocus()
  emit('startDebug', getPath(index))
}
defineExpose({
  changeFocus
})

</script>

<style scoped>
.editor-header-bar {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
  height: 25px;
  color: #dddddd;
}

.editor-header-bar-item {
  display: flex;
  align-items: center;
}

.editor-header-bar-item-separation {
  width: 1px;
  height: 30px;
  background-color: #ccccff;
}

.editor-base-container {
  height: 100%;
  width: 100%;
}

.debug-button {
  margin-right: 10px;
}

.editor-content {
  visibility: v-bind('fileItems?.length ? "visible" : "hidden"');
  height: calc(100% - 30px);
}
</style>

<template>
  <div class="editor-container">
    <EditorBase  ref="baseEditor" @save-file="saveCurrentFile" @start-debug="startDebug"> </EditorBase>

    <!-- <p>{{ fileItems }}</p>
    <p>{{ fileStatus }}</p> -->

  </div>
  <!-- 这里是要直接用在 View 里面的 Editor，作为拥有者管理各个 Editor 的状态 -->
  <!-- 使用 provide / inject 穿透祖先关系，直接获得 model 和 mapinformation -->
</template>

<script setup lang="ts">
import * as common from './common'
import EditorBase from './EditorBase.vue'
import { provide, ref, shallowRef, defineExpose, defineEmits, onUnmounted } from 'vue'
import * as monaco from 'monaco-editor/esm/vs/editor/editor.api'

export interface FileInfo {
  path: string,
  focus: boolean
}

export interface FileStatus {
  modified: boolean,
  openCount: number
}

export interface FileModel {
  model: monaco.editor.ITextModel,
}

// eslint-disable-next-line func-call-spacing
const emit = defineEmits<{
  (e : 'saveFile', path: string, value: string) : void,
  (e : 'startDebug', path: string) : void,
}>()

const baseEditor = ref<InstanceType<typeof EditorBase> | null>(null)

// 和 tab 绑定
const fileItems = ref <Array<FileInfo>>(new Array<FileInfo>())

// 和 文件 绑定
const fileStatus = ref <Map<string, FileStatus>>(new Map<string, FileStatus>())
const fileModels = shallowRef <Map<string, FileModel>>(new Map<string, FileModel>())

function addFile (path: string, value: string) {
  console.log('addFile', path)
  if (!fileStatus.value.has(path)) {
    fileStatus.value.set(path, {
      modified: false,
      openCount: 1
    })
  } else {
    // 已经在某处打开了，就直接移动
    changeFocusToFile(path)
    return
    // const status = fileStatus.value.get(path) as FileStatus
    // status.openCount++
    // fileStatus.value.set(path, status)
  }
  if (!fileModels.value.has(path)) {
    fileModels.value.set(path, {
      model: monaco.editor.createModel(value, undefined, monaco.Uri.file(path))
    })
  }
  fileItems.value.push({ path, focus: false })
  baseEditor.value?.changeFocus(fileItems.value.length - 1)
}

function saveCurrentFile () {
  const current = fileItems.value.find((item) => item.focus)
  if (current) {
    const model = fileModels.value.get(current.path) as FileModel
    emit('saveFile', current.path, model.model.getValue())
  }
}

// change to first occurence
function changeFocusToFile (path : string, line?: number) {
  const index = fileItems.value.findIndex((item) => item.path === path)
  baseEditor.value?.changeFocus(index, line)
}

function getBreakpoints () {
  const breakpoints = new Map<string, Array<number>>()
  fileModels.value.forEach((value, key) => {
    const model = value.model
    console.log(model.getAllDecorations())
    const lines = model.getAllDecorations().filter((item) => item.options.glyphMarginClassName === common.breakPointClassName).map((item) => item.range.startLineNumber)
    breakpoints.set(key, lines)
  })
  return breakpoints
}

function clearFocusLine () {
  fileModels.value.forEach((value) => {
    const model = value.model
    const decorations = model.getAllDecorations().filter((item) => item.options.className === common.focusLineClassName)
    model.deltaDecorations(decorations.map((item) => item.id), [])
  })
}

function focusLine (path : string, line : number) {
  // clear all focus line
  // quit if line is not in the range
  const model = fileModels.value.get(path) as FileModel
  const lineCount = model.model.getLineCount()
  if (line < 1 || line > lineCount) {
    console.error('line out of range')
    return
  }

  const decoration = {
    range: new monaco.Range(line, 1, line, 1),
    options: {
      isWholeLine: true,
      className: common.focusLineClassName,
      stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges
    }
  }
  model.model.deltaDecorations([], [decoration])
  changeFocusToFile(path, line)
}

function startDebug (file: string) {
  console.log('editor panel' + file)
  emit('startDebug', file)
}

// tmpAddFile('a.py', 'print("hello world test1")')
// tmpAddFile('b.py', 'print("hello world test2")')
// tmpAddFile('c.py', 'print("hello world test3")')

onUnmounted(() => {
  fileModels.value.forEach((value) => {
    value.model.dispose()
  })
})

provide('fileStatus', fileStatus)
provide('fileItems', fileItems)
provide('fileModels', fileModels)

defineExpose({
  addFile,
  changeFocusToFile,
  getBreakpoints,
  focusLine,
  clearFocusLine
})
</script>

<style>
.editor-container {
  height: 100%;
  width: 100%;
}
</style>

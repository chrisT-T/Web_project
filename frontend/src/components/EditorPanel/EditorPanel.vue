<template>
  <div class="general-editor-container">
    <GeneralEditor :file-tree="fileTree" class="editor-panel" ref="thisGeneralEditor"
      @delete-window="handleDeleteWindow"
      @add-window="handleAddWindow"
      @change-cursor-focus-window="handleChangeCursorFocus">
    </GeneralEditor>

    <p>{{ JSON.stringify(fileTree , null, 4) }}</p>
    <p>{{ fileItems }}</p>
    <p>{{ fileModels.keys() }}</p>
    <p>{{ fileStatus }}</p>

  </div>
  <!-- 这里是要直接用在 View 里面的 Editor，作为拥有者管理各个 Editor 的状态 -->
  <!-- 使用 provide / inject 穿透祖先关系，直接获得 model 和 mapinformation -->
</template>

<script setup lang="ts">
import GeneralEditor from './GeneralEditor.vue'
import { provide, ref, shallowRef, defineExpose } from 'vue'
import * as monaco from 'monaco-editor/esm/vs/editor/editor.api'

export interface FileInfo {
  path: string,
  title: string,
  focus: boolean
}

export interface FileTree {
  id: number,
  isLeaf: boolean,
  children: Array<FileTree>
  direction?: 'horizontal' | 'vertical',
}

export interface FileStatus {
  modified: boolean,
  openCount: number
}

export interface FileModel {
  model: monaco.editor.ITextModel,
}

const fileTree = ref<FileTree>({
  id: 0,
  isLeaf: false,
  direction: 'horizontal',
  children: [
    {
      id: 1,
      isLeaf: false,
      direction: 'vertical',
      children: [
        {
          id: 2,
          isLeaf: true,
          children: []
        },
        {
          id: 3,
          isLeaf: true,
          children: []
        }
      ]
    }, {
      id: 4,
      isLeaf: true,
      children: []
    }
  ]
})

const thisGeneralEditor = shallowRef<InstanceType<typeof GeneralEditor> | null>(null)

// 和 tab 绑定
const fileItems = ref <Map<number, Array<FileInfo>>>(new Map<number, Array<FileInfo>>())

// 和 文件 绑定
const fileStatus = ref <Map<string, FileStatus>>(new Map<string, FileStatus>())
const fileModels = shallowRef <Map<string, FileModel>>(new Map<string, FileModel>())

const currentCursorFocus = ref<Array<number>>([])

function addFile (path: string, value: string) {
  const model = monaco.editor.createModel(value, 'python')
  if (!fileModels.value.has(path)) {
    fileModels.value.set(path, { model })
  }
  if (!fileStatus.value.has(path)) {
    fileStatus.value.set(path, { modified: false, openCount: 0 })
  }
  if (currentCursorFocus.value.length === 0) {
    addFileToWindow(path, new Array<number>(1000).fill(0))
  } else {
    addFileToWindow(path, currentCursorFocus.value)
  }
}

function addFileToWindow (path : string, array : Array<number>) {
  thisGeneralEditor.value?.addFileToWindow(path, array)
}

function handleDeleteWindow (array: Array<number>) {
  if (array.length === 0) {
    // 删麻了，不用处理一下（）
  } else {
    deleteWindow(fileTree.value, array.reverse())
  }
  console.log(fileTree.value.children?.length)
}

function handleAddWindow (path : string, array : Array<number>) {
  if (array.length === 0) {
    // some ... temporary solution
    // TO BE DONE!
    array = new Array(1000).fill(0)
  }
  // random a newid or sequence id
  const newId = Math.floor(Math.random() * 1e9)
  fileItems.value.set(newId, [{
    path,
    title: path.split('/').pop() as string,
    focus: false
  }])
  const newOpenCount = fileStatus.value.get(path)?.openCount as number + 1
  fileStatus.value.set(path, { modified: false, openCount: newOpenCount })
  addWindow(fileTree.value, newId, array.reverse())
}

function handleChangeCursorFocus (array: Array<number>) {
  currentCursorFocus.value = array.reverse()
}

function deleteWindow (currentTree: FileTree, array: Array<number>) {
  if (array.length === 1) {
    currentTree.children?.splice(array[0], 1)
  } else {
    deleteWindow(currentTree.children?.[array[0]] as FileTree, array.slice(1))
  }
}

function addWindow (currentTree: FileTree, id : number, array: Array<number>) {
  if (currentTree.isLeaf === true || array.length === 1) {
    currentTree.children?.splice(array[0] + 1, 0, {
      id,
      isLeaf: true,
      children: []
    })
  } else {
    addWindow(currentTree.children?.[array[0]] as FileTree, id, array.slice(1))
  }
}

fileStatus.value.set('a', {
  modified: false,
  openCount: 1
})

fileStatus.value.set('b', {
  modified: false,
  openCount: 1
})

fileStatus.value.set('c', {
  modified: false,
  openCount: 1
})

fileStatus.value.set('d', {
  modified: false,
  openCount: 1
})

fileStatus.value.set('e', {
  modified: false,
  openCount: 1
})

fileItems.value.set(0, [])

fileItems.value.set(2, [
  {
    path: 'a',
    title: 'a',
    focus: false
  }
])

fileItems.value.set(3, [
  {
    path: 'b',
    title: 'b',
    focus: false
  },
  {
    path: 'c',
    title: 'c',
    focus: false
  }
])

fileItems.value.set(4, [
  {
    path: 'd',
    title: 'd',
    focus: false
  },
  {
    path: 'e',
    title: 'e',
    focus: false
  }
])

fileModels.value.set('a', {
  model: monaco.editor.createModel('a', 'python')
})

fileModels.value.set('b', {
  model: monaco.editor.createModel('b', 'python')
})

fileModels.value.set('c', {
  model: monaco.editor.createModel('c', 'python')
})

fileModels.value.set('d', {
  model: monaco.editor.createModel('d', 'python')
})

fileModels.value.set('e', {
  model: monaco.editor.createModel('e', 'python')
})

provide('fileStatus', fileStatus.value)
provide('fileItems', fileItems.value)
provide('fileModels', fileModels.value)

defineExpose({
  addFile
})
</script>

<style>
.general-editor-container {
  height: 100%;
  width: 100%;
  background-color: #6D6D6D;
;
}
</style>

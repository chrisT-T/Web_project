<template>
  <div class="general-editor-container">
    <GeneralEditor :file-tree="fileTree" class="editor-panel" @delete-window="handleDeleteWindow"></GeneralEditor>
  </div>
  <!-- 这里是要直接用在 View 里面的 Editor，作为拥有者管理各个 Editor 的状态 -->
  <!-- 使用 provide / inject 穿透祖先关系，直接获得 model 和 mapinformation -->
</template>

<script setup lang="ts">
import GeneralEditor from './GeneralEditor.vue'
import { provide, ref, shallowRef, ShallowRef } from 'vue'
import * as monaco from 'monaco-editor/esm/vs/editor/editor.api'

export interface FileInfo {
  path: string,
  title: string,
  focus: boolean
}

export interface FileTree {
  id: number,
  isLeaf: boolean,
  direction?: 'horizontal' | 'vertical',
  children?: Array<FileTree>
}

export interface FileStatus {
  modified: boolean
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
          isLeaf: true
        },
        {
          id: 3,
          isLeaf: true
        }
      ]
    }, {
      id: 4,
      isLeaf: true
    }
  ]
})

function handleDeleteWindow (array: Array<number>) {
  console.log(array)
  if (array.length === 0) {
    // TO BE ADD ?
  } else {
    deleteWindow(fileTree.value, array)
  }
}

function deleteWindow (currentTree : FileTree, array : Array<number>) {
  if (array.length === 1) {
    currentTree.children?.splice(array[0], 1)
  } else {
    deleteWindow(currentTree.children?.[array[0]] as FileTree, array.slice(1))
  }
}

// fileContents 是一个 Map，key 是 path，value 是 FileContent
const fileStatus = ref <Map<string, FileStatus>>(new Map<string, FileStatus>())
// fileItems 是从 ID 到 Array<FileInfo> 的映射
const fileItems = ref <Map<number, Array<FileInfo>>>(new Map<number, Array<FileInfo>>())

const fileModels = shallowRef <Map<string, FileModel>>(new Map<string, FileModel>())

fileStatus.value.set('a', {
  modified: false
})

fileStatus.value.set('b', {
  modified: false
})

fileStatus.value.set('c', {
  modified: false
})

fileStatus.value.set('d', {
  modified: false
})

fileStatus.value.set('e', {
  modified: false
})

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

</script>

<style>
.general-editor-container {
  height: 100%;
  width: 100%;
  background-color: #6D6D6D;
;
}
</style>

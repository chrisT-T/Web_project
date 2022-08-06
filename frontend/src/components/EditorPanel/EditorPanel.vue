<template>
  <div class="general-editor-container">
    <GeneralEditor :window-id="rootID" class="editor-panel" ref="thisGeneralEditor"
      @delete-window="handleDeleteWindow"
      @add-window="handleAddWindow"
      @change-cursor-focus-window="handleChangeCursorFocus">
    </GeneralEditor>

    <p>{{ fileTrees }}</p>
    <p>{{ fileItems }}</p>
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
  focus: boolean
}

export interface FileTree {
  id: number,
  isLeaf: boolean,
  parent: number,
  children: Array<number>
  direction?: 'horizontal' | 'vertical',
}

export interface FileStatus {
  modified: boolean,
  openCount: number
}

export interface FileModel {
  model: monaco.editor.ITextModel,
}

const thisGeneralEditor = shallowRef<InstanceType<typeof GeneralEditor> | null>(null)

// root is at number 0
const undefinedID = -1
const rootID = 0
const fileTrees = ref<Map<number, FileTree>>(new Map())

fileTrees.value.set(rootID, {
  id: rootID,
  isLeaf: false,
  parent: undefinedID,
  children: [],
  direction: 'horizontal'
})

// 和 tab 绑定
const fileItems = ref <Map<number, Array<FileInfo>>>(new Map<number, Array<FileInfo>>())

// 和 文件 绑定
const fileStatus = ref <Map<string, FileStatus>>(new Map<string, FileStatus>())
const fileModels = shallowRef <Map<string, FileModel>>(new Map<string, FileModel>())

// 记录 window 的 ID
const currentCursorFocus = ref<number>()

function addFile (path: string, value: string) {
  const model = monaco.editor.createModel(value, 'python')
  if (!fileModels.value.has(path)) {
    fileModels.value.set(path, { model })
  }
  if (!fileStatus.value.has(path)) {
    fileStatus.value.set(path, { modified: false, openCount: 1 })
  }
  if (currentCursorFocus.value) {
    addFileToWindow(currentCursorFocus.value as number, path)
  } else {
    const firstWindowID = getFirstWindow(0)
    if (firstWindowID !== undefinedID) {
      addFileToWindow(firstWindowID, path)
    } else {
      handleAddWindow(rootID, 'horizontal')
      addFileToWindow(getFirstWindow(rootID) as number, path)
    }
  }
}

function getFirstWindow (currentID: number) : number {
  const currentTree = fileTrees.value.get(currentID)
  if (currentTree) {
    if (currentTree.isLeaf) {
      return currentID
    } else {
      return getFirstWindow(currentTree.children[0])
    }
  } else {
    return undefinedID
  }
}

function addFileToWindow (windowID: number, path : string) {
  console.log('here!!!')
  const fileItem = fileItems.value.get(windowID)
  if (fileItem) {
    fileItem.push({ path, focus: false })
    fileItems.value.set(windowID, fileItem)
  } else {
    fileItems.value.set(windowID, [{ path, focus: false }])
  }
}

function handleDeleteWindow (windowID : number) {
  const parentID = fileTrees.value.get(windowID)?.parent as number
  // only one children
  if (parentID !== rootID && fileTrees.value.get(parentID)?.children.length === 1) {
    // recursive delete
    handleDeleteWindow(parentID)
  } else {
    const parent = fileTrees.value.get(parentID) as FileTree
    parent.children.splice(parent.children.indexOf(windowID) as number, 1)
  }
  fileItems.value.delete(windowID)
  fileTrees.value.delete(windowID)
}

function handleAddWindow (windowID : number, direction: 'horizontal' | 'vertical') {
  console.log('add window', windowID)
  const newWindowID = Math.floor(Math.random() * 1e9)

  const parentID = fileTrees.value.get(windowID)?.parent as number
  if (parentID !== undefinedID) {
    // not a root
    if (fileTrees.value.get(parentID)?.direction === direction) {
      // same direction --> as a sibling
      fileTrees.value.set(newWindowID, {
        id: newWindowID,
        isLeaf: true,
        parent: parentID,
        children: []
      })
      const parent = fileTrees.value.get(parentID) as FileTree
      const index = parent.children.indexOf(windowID)
      parent.children.splice(index + 1, 0, newWindowID)
    } else {
      // different direction --> as a child
      // generate a new parent
      const newParentID = Math.floor(Math.random() * 1e9)
      const oldParent = fileTrees.value.get(parentID) as FileTree
      oldParent.children.splice(oldParent.children.indexOf(windowID), 1, newParentID)
      // replace parent's son with a new parent
      fileTrees.value.set(parentID, oldParent)
      fileTrees.value.set(newParentID, {
        id: newParentID,
        isLeaf: false,
        parent: parentID,
        children: [windowID, newWindowID],
        direction
      })
      fileTrees.value.set(windowID, {
        id: windowID,
        isLeaf: true,
        parent: newParentID,
        children: []
      })
      fileTrees.value.set(newWindowID, {
        id: newWindowID,
        isLeaf: true,
        parent: newParentID,
        children: []
      })
    }
  } else {
    fileTrees.value.set(newWindowID, {
      id: newWindowID,
      isLeaf: true,
      parent: rootID,
      children: []
    })
    fileTrees.value.set(rootID, {
      id: rootID,
      isLeaf: false,
      parent: undefinedID,
      children: [newWindowID],
      direction
    })
  }

  // set fileItems
  const newfileInfo = fileItems.value.get(windowID)?.filter((item) => item.focus)[0] as FileInfo
  const newfileStatus = fileStatus.value.get(newfileInfo.path) as FileStatus
  newfileStatus.openCount += 1
  fileStatus.value.set(newfileInfo.path, newfileStatus)
  fileItems.value.set(newWindowID, [
    {
      path: newfileInfo.path,
      focus: true
    }
  ])
}

function handleChangeCursorFocus (windowID : number) {
  currentCursorFocus.value = windowID
}

fileTrees.value.set(0, {
  id: 0,
  isLeaf: false,
  parent: -1,
  direction: 'vertical',
  children: [1, 2]
}).set(1, {
  id: 1,
  isLeaf: true,
  parent: 0,
  children: []
}).set(2, {
  id: 2,
  isLeaf: true,
  parent: 0,
  children: []
})

function tmpAddFile (path :string, value :string) {
  fileStatus.value.set(path, { modified: false, openCount: 1 })
  fileModels.value.set(path, { model: monaco.editor.createModel(value, 'python') })
}

tmpAddFile('a.py', 'print("hello world test1")')
tmpAddFile('b.py', 'print("hello world test2")')
tmpAddFile('c.py', 'print("hello world test3")')

fileItems.value.set(1, [
  {
    path: 'a.py',
    focus: false
  }
])

fileItems.value.set(2, [
  {
    path: 'b.py',
    focus: false
  },
  {
    path: 'c.py',
    focus: false
  }
])

provide('fileTrees', fileTrees.value)
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

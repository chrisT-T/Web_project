<template>
  <!-- 在这里完成编辑器组件的递归 / 嵌套，最后进入 EditorBase 成为单个实例，解除递归 -->
  <!-- 还要记得加上拖拽的边界功能（） -->
  <!-- 功能：1. 递归 2. 传递 message 到上层 （自上而下的更新可以由 Reactive 代劳？） -->
  <template v-if="fileTree.isLeaf">
    <!-- 是 Leaf 了！ -->
    <EditorBase :id="fileTree.id" ref="baseEditor"
      @delete-editor="emit('deleteWindow', fileTree.id)"
      @split-current-view="(direction: 'horizontal' | 'vertical') => { emit('addWindow', fileTree.id, direction) }"
      @change-cursor-focus="() => {emit('changeCursorFocusWindow', fileTree.id)}">
      ></EditorBase>
  </template>
  <template v-else>
    <!-- 不是 leaf，需要遍历构造 child -->
    <splitpanes :horizontal="fileTree.direction === 'horizontal'">
      <pane v-for="child in fileTree.children" :key="child" min-size="20">
        <GeneralEditor :window-id="child"
          @add-window="(windowID: number, direction: 'horizontal' | 'vertical') => { emit('addWindow', windowID, direction) }"
          @delete-window="(windowID: number) => { emit('deleteWindow', windowID) }"
          @change-cursor-focus-window="(windowID: number) => {emit('changeCursorFocusWindow', windowID)}">
        </GeneralEditor>
      </pane>
    </splitpanes>
  </template>
</template>

<script setup lang="ts">
import { shallowRef, defineProps, defineEmits, inject } from 'vue'
import { FileTree } from './EditorPanel.vue'
import EditorBase from './EditorBase.vue'
import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'

const fileTrees = inject('fileTrees') as Map<number, FileTree>

const props = defineProps<{
  windowId: number,
}>()

const fileTree = fileTrees.get(props.windowId) as FileTree

console.log(fileTrees.get(props.windowId))

// sorry, but I have to do that
const baseEditor = shallowRef<InstanceType<typeof EditorBase> | null>(null)

// eslint-disable-next-line func-call-spacing
const emit = defineEmits<{
  (e: 'deleteWindow', windowID: number): void,
  (e: 'addWindow', windowId: number, direction: 'horizontal' | 'vertical'): void,
  (e: 'changeCursorFocusWindow', windowID: number): void,
}>()

</script>

<style>
.splitpanes--vertical>.splitpanes__splitter {
  min-width: 3px;
}

.splitpanes--vertical>.splitpanes__splitter:hover {
  background-color: #0000cc;
  outline: #0000cc solid;
  outline-width: 3px 0px;
}
.splitpanes--horizontal>.splitpanes__splitter:hover {
  background-color: #0000cc;
  outline: #0000cc solid;
  outline-width: 3px 0px;
  z-index: 1;
}

.splitpanes--horizontal>.splitpanes__splitter {
  min-height: 3px;
}
</style>

<script lang="ts">
// use normal <script> to declare options
export default {
  inheritAttrs: false
}
</script>

<template>
  <!-- 这个是单个的“编辑器”，包括上面的文件 header 和导航栏？-->
  <div>
    <EditHeader></EditHeader>
    <MonacoEditor :editor-option="monacoEditorOption"></MonacoEditor>
  </div>
</template>

<script lang="ts" setup>
import EditHeader from './Header/EditorHeader.vue'
import MonacoEditor from './MonacoEditor/MonacoEditor.vue'
const monacoEditorOption = {
  theme: 'vs-dark',
  glyphMargin: true,
  language: 'python'
}
</script>

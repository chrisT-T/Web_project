<template>
<el-tabs v-model="activeName" class="demo-tabs" tab-position="left">
  <el-tab-pane label="Debugger" name="first">
    <web-debugger :key='debuggerPath' :file-path='debuggerPath' ref="tDebugger" v-bind="$attrs"></web-debugger>
  </el-tab-pane>
  <el-tab-pane label="Terminal" name="second">
    <terminal-panel ref="terminalPanels" @get-pdb-port="initDbger"></terminal-panel>
  </el-tab-pane>
</el-tabs>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
const debuggerPath = ref<string>('')
const activeName = ref('first')
const tDebugger = ref()
const terminalPanels = ref()

function initDbger (port: number) {
  tDebugger.value.initDebugger(port)
}

function setDebuggerPath (path: string) {
  debuggerPath.value = path
}

function startDebuggerTerminal () {
  terminalPanels.value.startDebuggerTerminal()
}

defineExpose({
  setDebuggerPath,
  startDebuggerTerminal
})
</script>

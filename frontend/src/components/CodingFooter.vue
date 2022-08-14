<template>
<el-tabs v-model="activeName" class="demo-tabs" tab-position="left">
  <el-tab-pane label="Terminal" name="first">
    <terminal-panel ref="terminalPanels" @get-pdb-port="initDbger"></terminal-panel>
  </el-tab-pane>
  <el-tab-pane label="Debugger" name="second">
    <web-debugger :file-path='debuggerPath' :user-path="userPath" ref="tDebugger" v-bind="$attrs"></web-debugger>
  </el-tab-pane>
</el-tabs>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
const debuggerPath = ref<string>('')
const userPath = ref<string>('')
const activeName = ref('first')
const tDebugger = ref()
const terminalPanels = ref()
function initDbger (port: number) {
  tDebugger.value.initDebugger(port)
}

function setDebuggerPath (path: string, user: string) {
  debuggerPath.value = path
  userPath.value = user
}

function setBreakPoints (tBreakPoints: Map<string, number[]>) {
  console.log(tBreakPoints)
  tDebugger.value.setBreakPoints(tBreakPoints)
}

function startDebuggerTerminal () {
  terminalPanels.value.startDebuggerTerminal()
}

defineExpose({
  setDebuggerPath,
  setBreakPoints,
  startDebuggerTerminal
})
</script>

<style scoped>
.demo-tabs :deep(.is-active.el-tabs__item),.demo-tabs :deep(.el-tabs__item:hover){
  color: white;
}

.demo-tabs :deep(.el-tabs__item){
  color: black;
}
.demo-tabs :deep(.el-tabs__active-bar) {
  background-color: var(--el-color-primary-light-3);
}

</style>

<template>
  <div class="common-layout">
    <el-container>
      <el-header>
        <el-button type="primary" class="backBtn" :icon="HomeFilled" @click="ProjectBack" text>Menu</el-button>
        <el-button type="primary" class="saveBtn" :icon="Checked" @click="saveProject" text>Save</el-button>
      </el-header>
      <el-container>
        <div class="btnArea">
          <el-button class="closeBtn" :icon="Fold" @click="closeAside" circle />
        </div>
        <el-aside :width="data.width">
          <el-tabs v-model="sidebarActiveName" tab-position="left" class="aside-tabs">
            <el-tab-pane label="File" name="first">
              <FileSet :name="name" :projectname="projectname" @debug-start="(path) => runDebugger(path)" @open-file="openFile"></FileSet>
            </el-tab-pane>
            <el-tab-pane label="Debug" name="second">
              <div style="display: flex;flex-direction: column;width: 100%">
                <DebugSideBar ref="tDebugSideBar" token="1" @update-focus-line="updateFocusLine"></DebugSideBar>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-aside>
        <span class="resize_col" @mousedown="handleDragStart"></span>
        <el-container>
          <div class="dbg_panel" ref="dbgPanel">
            <span class="dbg_panel_handle" @mousedown="dragDebugPanel" />
            <debug-buttons ref="dbgButtons" v-if="isDebugging" @runcmd-with-break-point="runcmdWithBreakPoint" @restart-debugger="restartDebugger"></debug-buttons>
          </div>
          <splitpanes class="default-theme" horizontal>
            <pane>
              <EditorPanel ref="editorPanel" @save-file="saveFile"></EditorPanel>
            </pane>
            <pane min-size="20">
              <el-footer>
                <coding-footer ref="tFooter" @disconnect="hideButtons" @init-button="activateButtons" @debugger-data-update="updateDebuggerSideBar" @ended="cleanEditorFocus"></coding-footer>
              </el-footer>
            </pane>
          </splitpanes>
        </el-container>
      </el-container>
    </el-container>
  </div>
</template>

<script lang="ts" setup>
import router from '@/router'
import { ref, reactive, nextTick, h } from 'vue'
import { useRouter } from 'vue-router'
import {
  Fold,
  HomeFilled,
  Checked
} from '@element-plus/icons-vue'
import axios from 'axios'

import FileSet from '../components/fileSet.vue'
import { ElNotification } from 'element-plus'
import EditorPanel from '@/components/EditorPanel/EditorPanel.vue'
import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'
import DebugSideBar from '../components/DebugSideBar.vue'
import CodingFooter from '../components/CodingFooter.vue'
import DebugButtons from '../components/DebugButtons.vue'

// 获取当前用户名
const name = useRouter().currentRoute.value.params.username

// 获取当前项目名
const projectname = useRouter().currentRoute.value.params.projectname

// 获取 EditorPanel 的 ref
const editorPanel = ref<InstanceType<typeof EditorPanel> | null>(null)

// 回到当前用户的项目管理区域
const ProjectBack = () => {
  router.replace({ name: 'projectmanage', params: { username: name } })
}

const data = reactive({
  width: '300px',
  old_width: '0px',
  isClose: false,
  originX: 200,
  originY: 20,
  height: '300px',
  old_height: '0px',
  old_height_2: 0,
  height_2: 50
})

// 侧边栏收开
const closeAside = () => {
  if (data.isClose) {
    console.log('isClose')
    data.width = data.old_width
    data.isClose = false
    console.log(data.isClose)
  } else {
    console.log('noClose')
    data.old_width = data.width
    data.width = '0px'
    data.isClose = true
    console.log(data.isClose)
  }
}

// 保存文件
const saveProject = () => {
  console.log('save')
}

// 侧边栏拖拽大小
const handleDragStart = (event: MouseEvent) => {
  data.originX = event.clientX
  console.log(data.originX)
  let isMouseDown = true
  document.onmousemove = (ev:MouseEvent) => {
    if (!isMouseDown) return false
    const moveX = ev.clientX
    console.log(ev.clientX, data.originX, moveX)
    data.old_width = data.width
    data.width = moveX + 'px'
  }
  document.onmouseup = () => {
    if (!isMouseDown) return false
    isMouseDown = false
  }
}

function saveFile (path: string, value: string) {
  console.log(path, value)
  axios.post(`/api/upload/${name}`, {
    src: path,
    text: value
  }).then((res) => {
    console.log(res)
    ElNotification({
      title: 'Success',
      message: '保存成功',
      type: 'success'
    })
  }).catch((err) => {
    console.log(err)
    ElNotification({
      title: 'Error',
      message: '保存失败',
      type: 'error'
    })
  })
}

function openFile (path: string) {
  console.log(path)
  axios.get(`/api/download/${name}`, {
    params: {
      src: path
    }
  }).then((res) => {
    console.log(res)
    editorPanel.value?.addFile(path, res.data.text)
  }).catch((err) => {
    console.log(err)
  })
}
const tFooter = ref()
const tDebugSideBar = ref()
const dbgButtons = ref()
const isDebugging = ref<boolean>(false)

function getBreakPoints (): Map<string, number[]> {
  return editorPanel.value?.getBreakpoints() as Map<string, number[]>
}

function runcmdWithBreakPoint (cmd: string) {
  dbgButtons.value.runcmd(cmd, getBreakPoints(), './userfile/' + name)
}

// run debugger
function runDebugger (filePath: string) {
  console.log('coding view ' + filePath)
  tFooter.value.setDebuggerPath('./userfile/' + filePath, './userfile/' + name)
  const breakPoints = editorPanel.value?.getBreakpoints()
  tFooter.value.setBreakPoints(breakPoints)
  tFooter.value.startDebuggerTerminal()
}

async function activateButtons (port: number, token: string) {
  isDebugging.value = true
  await nextTick()
  dbgButtons.value.init(port, token)
}
function hideButtons () {
  isDebugging.value = false
}

const dbgPanel = ref()

function dragDebugPanel (event : MouseEvent) {
  const offsetX = event.clientX - dbgPanel.value.offsetLeft
  document.onmousemove = function (eve : MouseEvent) {
    dbgPanel.value.style.left = eve.clientX - offsetX + 'px'
  }
  document.onmouseup = function () {
    document.onmousedown = null
    document.onmousemove = null
  }
}
const sidebarActiveName = ref('first')

function updateDebuggerSideBar (port: number, token: string) {
  console.log('update test', port)
  tDebugSideBar.value.updateData(port, token)
}

function updateFocusLine (lineno: number, path: string) {
  const relPath = path.replace('./userfile/' + name + '/', '')
  console.log(lineno, path, relPath)
  editorPanel.value?.clearFocusLine()
  try {
    editorPanel.value?.focusLine(relPath, lineno)
  } catch (e: TypeError) {
    ElNotification({
      title: 'Debugger Running',
      message: h('i', { style: 'color: teal' }, 'The Debugging file does not open in Editor')
    })
  }
}

function cleanEditorFocus () {
  editorPanel.value?.clearFocusLine()
}

function restartDebugger (port: number) {
  tFooter.value.initDbger(port, true)
}

defineExpose({
  getBreakPoints
})
</script>

<style scoped>
div {
  display: flex;
  height: 100%;
}
.el-header {
  background-color: var(--el-color-primary-dark-2);
  height: 30px;
  display: flex;
  flex-direction: row;
  padding: 0 5px;
}
.resize_col {
  cursor: col-resize;
  float: left;
  border-radius: 5px;
  width: 4px;
  background-color: var(--el-border-color-light);
}
.backBtn, .saveBtn {
  height: 30px;
  background-color: var(--el-color-primary-dark-2);
  color: aliceblue;
  margin: 0;
}
.backBtn:hover, .saveBtn:hover {
  color: black;
}
.backBtn:hover {
  background-color: var(--el-color-primary);
}
.el-footer {
  width: 100%;
  height: 100%;
  background-color: var(--el-color-primary-dark-2);
  /* overflow: auto; */
  display: flex;
  flex-direction: column;
  padding: 0;
}
.dbg_panel {
  position: absolute;
  height: 40px;
  left: 800px;
}
.dbg_panel_handle {
  margin-left: 6px;
  width: 4px;
  background-color: var(--el-border-color-light);;
  cursor: col-resize
}
.el-aside {
  overflow: auto;
}
.el-main {
  background-color: var(--el-color-primary-light-7);
  overflow: auto;
}
.btnArea {
  display: flex;
  flex-direction: column;
}
.btnArea .el-button {
  margin: 5px 2px;
}

.term_panel {
  width: 100%;
  height: 100vh;
}
:deep(.el-tabs__content) {
  width: 100%
}
</style>

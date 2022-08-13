<template>
  <div>
    <el-tabs v-model="activeName" class="demo-tabs" @tab-click="handleClick">
      <el-tab-pane label="Config" name="first">
        <splitpanes class="default-theme">
          <pane>
            <div class="debugConsole">
              <p style="text-align: left; font-size: 20px; font-weight: bold;"> Debug Console:</p>
              <p>{{ consoleOutput }}</p>
              <el-input  name="command" id="command" v-model="command" @keyup.enter="send" style="position: absolute; bottom: 0"/>
            </div>
          </pane>
          <pane>
            <p style="margin-bottom: 70px; font-weight: bold;">Current Line: {{curline}}</p>
            <div v-if="isDebugging" style="display: flex;">
              <el-icon @click="cont" title="Continue" :size="size"><CaretRight /></el-icon>
              <el-icon @click="next" title="Step Over" :size="size"><Right /></el-icon>
              <el-icon @click="stepInto" title="Step Into" :size="size"><Download /></el-icon>
              <el-icon @click="stepOut" title="Step Out" :size="size"><Upload /></el-icon>
              <el-icon @click="restart" title="Restart" :size="size"><RefreshLeft /></el-icon>
              <el-icon @click="stop" title="Stop" :size="size"><CloseBold /></el-icon>
            </div>
          </pane>
        </splitpanes>
      </el-tab-pane>
    </el-tabs>

  </div>
</template>

<script lang="ts" setup>

import { ref, onMounted } from 'vue'
import { Terminal } from 'xterm'
import io from 'socket.io-client'
import axios from 'axios'
import { FitAddon } from 'xterm-addon-fit'
import VariableTable from '@/components/VariableTable.vue'
import type { TabsPaneContext, Action } from 'element-plus'
import { Splitpanes, Pane } from 'splitpanes'
// element plus msg box
import { ElMessage, ElMessageBox } from 'element-plus'

const activeName = ref('first')

const handleClick = (tab: TabsPaneContext, event: Event) => {
  console.log(tab, event)
}

interface Tree {
  label: string
  children?: Tree[]
}
interface StackItem {
  func: string
  file: string
}

const props = defineProps({
  filePath: String,
  userPath: String
})

const size = 40 as number
let baseUrl = 'http://127.0.0.1:' as string
const command = ref(null)
const consoleOutput = ref(null)
const stk = ref<StackItem[]>([])
const variables = ref<Tree[]>([])
const curline = ref<number>(1)
const isDebugging = ref<boolean>(false)
let breakPoints = new Map<string, Array<number>>()
let pdbSocket = io()

const emit = defineEmits <{(e: 'debuggerDataUpdate', port: number, token: string): void}>()

function setBreakPoints (tBreakPoints: Map<string, number[]>) {
  breakPoints = tBreakPoints
  console.log(breakPoints)
}

function initDebugger (port: number) {
  baseUrl += port.toString()

  pdbSocket = io(baseUrl + '/pdb')

  pdbSocket.on('connect', () => {
    console.log('connect running', pdbSocket.id)
    console.log(breakPoints)
    axios.post(baseUrl + '/pdb/debug', { token: pdbSocket.id, filepath: props.filePath }).then(() => {
      isDebugging.value = true
    })
    breakPoints.forEach((value, key) => {
      value.forEach((lineno) => {
        console.log(key, lineno, `b ${props.userPath}/${key}: ${lineno}`)
        axios.post(baseUrl + '/pdb/runcmd', { token: pdbSocket.id, cmd: `b ${props.userPath}/${key}: ${lineno}` })
      })
    })
  })

  pdbSocket.on('pdb_quit', (data) => {
    pdbSocket.disconnect()
    variables.value = [] as Tree[]
    stk.value = [] as StackItem[]
    isDebugging.value = false
  })

  pdbSocket.on('pdb_output', (data: {'consoleOutput': string, 'token': string}) => {
    console.log(data)
    if (data.token === pdbSocket.id) {
      consoleOutput.value += data.consoleOutput
      console.log('consoleOutpu ', port)
      emit('debuggerDataUpdate', port, pdbSocket.id)
    }
  })
}

function cont () {
  axios.post(baseUrl + '/pdb/runcmd', { token: pdbSocket.id, cmd: 'c' })
}

function send () {
  console.log('pdb command send ' + baseUrl + '/pdb/runcmd')
  if (isDebugging.value === true) {
    axios.post(baseUrl + '/pdb/runcmd', { token: pdbSocket.id, cmd: command.value })
  } else {
    ElMessageBox.alert('Debugger is not running', 'Debug Error', {
      confirmButtonText: 'OK'
    })
  }
}

function next () {
  axios.post(baseUrl + '/pdb/runcmd', { token: pdbSocket.id, cmd: 'n' })
}

function stepInto () {
  axios.post(baseUrl + '/pdb/runcmd', { token: pdbSocket.id, cmd: 's' })
}

function stepOut () {
  axios.post(baseUrl + '/pdb/runcmd', { token: pdbSocket.id, cmd: 'u' })
}

function stop () {
  axios.post(baseUrl + '/pdb/runcmd', { token: pdbSocket.id, cmd: 'q' })
}

function restart () {
  axios.post(baseUrl + '/pdb/runcmd', { token: pdbSocket.id, cmd: 'q' })
  // axios.post (baseUrl + '/pdb/debug', { token: pdbSocket.id, filepath: filePath })
  pdbSocket = io()
}

function fit () {
  fitAddon.fit()
}

onMounted(() => {
  const resize = document.getElementsByClassName('resize')
  for (const i of resize) {
    i.addEventListener('mouseup', fit)
  }
})

defineExpose({
  initDebugger,
  setBreakPoints
})
</script>

<style scoped>
  @import 'xterm/css/xterm.css';
  @import 'splitpanes/dist/splitpanes.css';

  .debugConsole {
    white-space: pre;
    text-align: left;
    overflow-y: scroll;
    overflow-x: scroll;

  }
  .stkContainer {
    text-align: left;
  }
  .stkFunc {
    float: left;
  }
  .stkFile {
    float: right;
  }
  .termContainer {

  }
</style>

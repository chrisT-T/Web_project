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

import { ref, onMounted, h } from 'vue'
import io, { Socket } from 'socket.io-client'
import axios from 'axios'
import type { TabsPaneContext } from 'element-plus'
import { Splitpanes, Pane } from 'splitpanes'
// element plus msg box
import { ElMessageBox, ElNotification } from 'element-plus'

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
const isDebugging = ref<boolean>(false)
let breakPoints = new Map<string, Array<number>>()
let pdbSocket = null as Socket | null

const emit = defineEmits <{(e: 'debuggerDataUpdate', port: number, token: string): void}>()

function setBreakPoints (tBreakPoints: Map<string, number[]>) {
  breakPoints = tBreakPoints
  console.log(breakPoints)
}

function initDebugger (port: number) {
  baseUrl = 'http://127.0.0.1:' + port.toString()

  pdbSocket = io(baseUrl + '/pdb')
  console.log('initDebugger in webDebugger' + port)

  pdbSocket.on('connect', () => {
    console.log('connect running', pdbSocket?.id)
    console.log(breakPoints)
    axios.post(baseUrl + '/pdb/debug', { token: pdbSocket?.id, filepath: props.filePath }).then(() => {
      isDebugging.value = true
    })
    breakPoints.forEach((value, key) => {
      value.forEach((lineno) => {
        console.log(key, lineno, `b ${props.userPath}/${key}: ${lineno}`)
        axios.post(baseUrl + '/pdb/runcmd', { token: pdbSocket?.id, cmd: `b ${props.userPath}/${key}: ${lineno}` })
      })
    })
  })

  pdbSocket.on('pdb_quit', () => {
    pdbSocket?.disconnect()
    ElNotification({
      title: 'Debugger Quit',
      message: h('i', { style: 'color: teal' }, `The Debugger on port ${port} has quit`)
    })
    isDebugging.value = false
  })

  pdbSocket.on('pdb_output', (data: {'consoleOutput': string, 'token': string}) => {
    console.log(data)
    if (data.token === pdbSocket?.id) {
      consoleOutput.value += data.consoleOutput
      console.log('consoleOutpu ', port)
      emit('debuggerDataUpdate', port, pdbSocket?.id)
    }
  })

  pdbSocket.on('pdb_terminated', () => {
    pdbSocket?.disconnect()
    ElNotification({
      title: 'Debugger Terminated',
      message: h('i', { style: 'color: teal' }, `The Debugger on port ${port} was terminated`)
    })
    isDebugging.value = false
  })
}

function cont () {
  axios.post(baseUrl + '/pdb/runcmd', { token: pdbSocket?.id, cmd: 'c' })
}

function send () {
  console.log('pdb command send ' + baseUrl + '/pdb/runcmd', pdbSocket?.id)
  if (isDebugging.value === true) {
    axios.post(baseUrl + '/pdb/runcmd', { token: pdbSocket?.id, cmd: command.value })
  } else {
    ElMessageBox.alert('Debugger is not running', 'Debug Error', {
      confirmButtonText: 'OK'
    })
  }
}

function next () {
  axios.post(baseUrl + '/pdb/runcmd', { token: pdbSocket?.id, cmd: 'n' })
}

function stepInto () {
  axios.post(baseUrl + '/pdb/runcmd', { token: pdbSocket?.id, cmd: 's' })
}

function stepOut () {
  axios.post(baseUrl + '/pdb/runcmd', { token: pdbSocket?.id, cmd: 'u' })
}

function stop () {
  axios.post(baseUrl + '/pdb/runcmd', { token: pdbSocket?.id, cmd: 'q' })
}

function restart () {
  axios.post(baseUrl + '/pdb/runcmd', { token: pdbSocket?.id, cmd: 'q' })
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

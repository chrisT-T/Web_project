<template>
  <div class="debugConsole">
    <p style="text-align: left; font-size: 20px; font-weight: bold;"> Debug Console:</p>
    <p>{{ consoleOutput }}</p>
    <el-input class="command" name="command" id="command" v-model="command" @keyup.enter="send"/>
  </div>
</template>

<script lang="ts" setup>

import { ref, h } from 'vue'
import io, { Socket } from 'socket.io-client'
import axios from 'axios'
// element plus msg box
import { ElMessageBox, ElNotification } from 'element-plus'

const props = defineProps({
  filePath: String,
  userPath: String
})

const command = ref(null)
const consoleOutput = ref<string>('')
const isDebugging = ref<boolean>(false)
let breakPoints = new Map<string, Array<number>>()
let pdbSocket = null as Socket | null
let mPort = 0

const emit = defineEmits <{(e: 'debuggerDataUpdate', port: number, token: string): void,
  (e: 'initButton', port: number, token: string): void,
  (e: 'ended'): void,
}>()

function setBreakPoints (tBreakPoints: Map<string, number[]>) {
  breakPoints = tBreakPoints
  console.log(breakPoints)
}

function initDebugger (port: number, restart = false) {
  mPort = port
  if (restart === true) {
    pdbSocket?.disconnect()
  }

  pdbSocket = io('/debugger') // 这里是不想 connect 的...但他们的 sid 不一样...
  pdbSocket.on('connect', () => {
    pdbSocket?.emit('connect_to_debug_server', { port })
    console.log('connect to debugger server')
  })
  console.log(`initDebugger in webDebugger, port ${port}`)

  pdbSocket.on('connect_to_debug_server_success', () => {
    ElNotification({
      title: 'Debugger Running',
      message: h('i', { style: 'color: teal' }, `A Debugger running on port ${port}`)
    })
    emit('initButton', port, pdbSocket?.id as string)
    console.log('connect running', pdbSocket?.id)
    console.log(breakPoints)
    axios.post('/pdb/debug', { port, token: pdbSocket?.id, filepath: props.filePath }).then(() => {
      isDebugging.value = true
    })
    breakPoints.forEach((value, key) => {
      value.forEach((lineno) => {
        console.log(key, lineno, `b ${props.userPath}/${key}: ${lineno}`)
        axios.post('/pdb/runcmd', { port, token: pdbSocket?.id, cmd: `b ${props.userPath}/${key}: ${lineno}` })
      })
    })
  })

  pdbSocket.on('pdb_quit', (data) => {
    console.log('quit ' + pdbSocket?.id + ' ' + data.token)
    if (pdbSocket?.id === data.token) {
      pdbSocket?.emit('disconnect_from_debug_server', { port })
      ElNotification({
        title: 'Debugger Quit',
        message: h('i', { style: 'color: teal' }, `The Debugger on port ${port} has quit`)
      })
      isDebugging.value = false
      axios.post('/pdb/inputbyport', { port, cmd: '\x03' })
      emit('ended')
    }
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
    pdbSocket?.emit('disconnect_from_debug_server', { port })
    ElNotification({
      title: 'Debugger Terminated',
      message: h('i', { style: 'color: teal' }, `The Debugger on port ${port} was terminated`)
    })
    isDebugging.value = false
    emit('ended')
  })
}

function send () {
  console.log('pdb command send ' + '/pdb/runcmd', pdbSocket?.id)
  if (isDebugging.value === true) {
    axios.post('/pdb/runcmd', { port: mPort, token: pdbSocket?.id, cmd: command.value })
  } else {
    ElMessageBox.alert('Debugger is not running', 'Debug Error', {
      confirmButtonText: 'OK'
    })
  }
}

defineExpose({
  initDebugger,
  setBreakPoints
})
</script>

<style scoped>
  @import 'xterm/css/xterm.css';
  @import 'splitpanes/dist/splitpanes.css';

  .debugConsole {
    height: 100%;
    white-space: pre;
    text-align: left;
    overflow-y: scroll;
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
  .command {
    position: absolute;
    bottom: 2px;
    right: 10px;
    padding: 0 10px;
  }
</style>

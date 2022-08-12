<template>
  <div>
    <el-tabs v-model="activeName" class="demo-tabs" @tab-click="handleClick">
      <el-tab-pane label="Debugger Output" name="first">
        <drag-item>
          <div class="debugConsole">
            <p style="text-align: left; font-size: 20px; font-weight: bold;"> Debug Console:</p>
            <p>{{ consoleOutput }}</p>
            <p style="margin-bottom: 70px; font-weight: bold;">Current Line: {{curline}}</p>
            <el-input name="command" id="command" v-model="command" @keyup.enter="send" style="position: absolute; bottom: 0"/>
            <div style="display: flex; position: absolute; bottom: 30px; left: -6px">
              <el-icon @click="cont" title="Continue" :size="size"><CaretRight /></el-icon>
              <el-icon @click="next" title="Step Over" :size="size"><Right /></el-icon>
              <el-icon @click="stepInto" title="Step Into" :size="size"><Download /></el-icon>
              <el-icon @click="stepOut" title="Step Out" :size="size"><Upload /></el-icon>
              <el-icon @click="restart" title="Restart" :size="size"><RefreshLeft /></el-icon>
              <el-icon @click="stop" title="Stop" :size="size"><CloseBold /></el-icon>
            </div>
          </div>
        </drag-item>
      </el-tab-pane>
      <el-tab-pane label="Config" name="second">
        <drag-box style="width: 100%; height: 100%">
          <drag-item>
            <variable-table :data="variables"></variable-table>
          </drag-item>
          <drag-item class="stkContainer">
            <p style="text-align: left; font-size: 20px; font-weight: bold;"> Stack:</p>
            <div v-for="(item,index) in stk" :key="index">
              <span class="stkFunc">{{item.func}}</span><span class="stkFile" style="margin-right:5px;">{{item.file}}</span><br>
            </div>
          </drag-item>
        </drag-box>
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
import type { TabsPaneContext } from 'element-plus'

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
  filePath: String
})

const size = 40 as number
let baseUrl = 'http://127.0.0.1:' as string
const status = ref(null)
const command = ref(null)
const consoleOutput = ref(null)
const stk = ref<StackItem[]>([])
const fitAddon = new FitAddon()
const variables = ref<Tree[]>([])
const curline = ref<number>(1)

let pdbSocket = io()

function initDebugger (port: number) {
  baseUrl += port.toString()
  pdbSocket = io(baseUrl + '/pdb')

  pdbSocket.on('connect', () => {
    axios.post(baseUrl + '/pdb/debug', { token: pdbSocket.id, filepath: props.filePath }).then(() => {
      console.log('Pdbsocket Connected')
    })
  })

  pdbSocket.on('pdb_quit', (data) => {
    status.value = data.flag
    pdbSocket.disconnect()
    variables.value = [] as Tree[]
    stk.value = [] as StackItem[]
  })

  pdbSocket.on('pdb_output', (data: {'consoleOutput': string, 'token': string}) => {
    console.log(data)
    if (data.token === pdbSocket.id) {
      consoleOutput.value += data.consoleOutput
      console.log(consoleOutput)
      updateData()
    }
  })
}

function cont () {
  axios.post(baseUrl + '/pdb/runcmd', { token: pdbSocket.id, cmd: 'c' })
}

function send () {
  axios.post(baseUrl + '/pdb/runcmd', { token: pdbSocket.id, cmd: command.value })
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

function updateData () {
  axios.post(baseUrl + '/pdb/curframe', { token: pdbSocket.id })
    .then((response) => {
      const rawLocals = JSON.parse(response.request.response).locals
      const rawGlobals = JSON.parse(response.request.response).globals
      const locals = rawLocals.split('\n')
      const globals = rawGlobals.split('\n')
      variables.value = []
      const loc = { label: 'locals', children: [] } as Tree
      for (const i of locals) {
        (loc.children as Tree[]).push({ label: i, children: [] })
      }
      const glob = { label: 'global', children: [] } as Tree
      for (const i of globals) {
        (glob.children as Tree[]).push({ label: i, children: [] })
      }
      variables.value.push(loc)
      variables.value.push(glob)
      curline.value = JSON.parse(response.request.response).current_line
    })
  axios.post(baseUrl + '/pdb/getstack', { token: pdbSocket.id }).then(
    (response) => {
      const stklist = JSON.parse(response.request.response)
      stk.value = []
      for (let i = 1; i < stklist.length; i++) {
        const funct = stklist[i].match(/, code (\S*)>/)[1]
        let fil = stklist[i].match(/file '(\S*)'/)[1]
        if (/\//.test(fil)) {
          console.log('yes')
          fil = fil.match(/\/(\w*?).py/)[1] + '.py'
          console.log(fil)
        }
        stk.value.splice(0, 0, { func: funct, file: fil })
      }
    }
  )
}

function test () {
  fitAddon.fit()
}

onMounted(() => {
  const resize = document.getElementsByClassName('resize')
  for (const i of resize) {
    i.addEventListener('mouseup', test)
  }
})

defineExpose({
  initDebugger
})
</script>

<style scoped>
  @import 'xterm/css/xterm.css';
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

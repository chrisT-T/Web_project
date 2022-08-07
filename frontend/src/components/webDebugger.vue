<template>
  <div>
    <h1> {{ status }} </h1>
    <div class="termContainer">
      <div id="debugTerm"></div>
    </div>
    <div id = "debugConsole">
      <p>{{ consoleOutput }}</p>
    </div>
    <el-icon @click="cont" title="Continue" :size="size"><CaretRight /></el-icon>
    <el-icon @click="next" title="Step Over" :size="size"><Right /></el-icon>
    <el-icon @click="stepInto" title="Step Into" :size="size"><Download /></el-icon>
    <el-icon @click="stepOut" title="Step Out" :size="size"><Upload /></el-icon>
    <el-icon @click="restart" title="Restart" :size="size"><RefreshLeft /></el-icon>
    <button @click="updateVariables"> data </button>
    <input type="text" name="command" id="command" v-model="command" @keyup.enter="send">
  </div>
  <variable-table :data="variables"></variable-table>
</template>

<script lang="ts">
import { Vue, prop } from 'vue-class-component'
import { Terminal } from 'xterm'
import io from 'socket.io-client'
import axios from 'axios'
import { FitAddon } from 'xterm-addon-fit'
import VariableTable from '@/components/VariableTable.vue'

interface Tree {
  label: string
  children?: Tree[]
}

class webDebuggerProps {
  filePath: string = prop({
    required: true
  })

  components: object = {
    VariableTable
  }
}

export default class webDebugger extends Vue.with(webDebuggerProps) {
  size = 40 as number
  baseUrl = 'http://127.0.0.1:' as string
  status = 'distanced' as string
  command = '' as string
  consoleOutput = '' as string

  variables = [] as Tree[]

  term = new Terminal({
    cursorBlink: true,
    macOptionIsMeta: true
  })

  socket = io('http://127.0.0.1:5000/pdb')

  pdbSocket = io()

  initDebugger () {
    this.term.open(document.getElementById('debugTerm') as HTMLElement)
    this.term.writeln('Debugger Terminal\n')
    this.term.onData((data) => {
      this.socket.emit('debugger_term_input', { input: data, token: this.pdbSocket.id })
    })

    this.socket.on('debugger_port', (data: {'port': number, 'token': string}) => {
      console.log(data)
      console.log(this.socket.id)
      this.baseUrl += data.port.toString()

      this.pdbSocket = io(this.baseUrl + '/pdb')

      this.pdbSocket.on('connect', () => {
        axios.post(this.baseUrl + '/pdb/debug', { token: this.pdbSocket.id, filepath: this.filePath }).then(() => {
          console.log('')
        })
      })

      this.pdbSocket.on('pdb_quit', (data) => {
        this.status = data.flag
        this.pdbSocket.disconnect()
        this.socket.disconnect()
        this.variables = [] as Tree[]
      })

      this.pdbSocket.on('pdb_output', (data: {'consoleOutput': string, 'token': string}) => {
        console.log(data)
        if (data.token === this.pdbSocket.id) {
          this.consoleOutput += data.consoleOutput
          this.updateVariables()
        }
      })
    })

    this.socket.on('debugger_term_output', (data: {'output': string, 'token': string}) => {
      console.log(data)
      this.term.write(data.output)
    })
    setTimeout(() => {
      this.term.clear()
    }, 2000)
  }

  cont () {
    axios.post(this.baseUrl + '/pdb/runcmd', { token: this.pdbSocket.id, cmd: 'c' })
  }

  send () {
    axios.post(this.baseUrl + '/pdb/runcmd', { token: this.pdbSocket.id, cmd: this.command })
  }

  next () {
    axios.post(this.baseUrl + '/pdb/runcmd', { token: this.pdbSocket.id, cmd: 'n' })
  }

  stepInto () {
    axios.post(this.baseUrl + '/pdb/runcmd', { token: this.pdbSocket.id, cmd: 's' })
  }

  stepOut () {
    axios.post(this.baseUrl + '/pdb/runcmd', { token: this.pdbSocket.id, cmd: 'u' })
  }

  restart () {
    // axios.post(this.baseUrl + '/pdb/runcmd', { token: this.pdbSocket.id, cmd: 'q' })
    // axios.post (this.baseUrl + '/pdb/debug', { token: this.pdbSocket.id, filepath: this.filePath })
    this.term.dispose()
    this.term = new Terminal({
      cursorBlink: true,
      macOptionIsMeta: true
    })
    this.socket = io('http://127.0.0.1:5000/pdb')
    this.initDebugger()
  }

  updateVariables () {
    axios.post(this.baseUrl + '/pdb/curframe', { token: this.pdbSocket.id })
      .then((response) => {
        const rawLocals = JSON.parse(response.request.response).locals
        const rawGlobals = JSON.parse(response.request.response).globals
        const locals = rawLocals.split('\n')
        const globals = rawGlobals.split('\n')
        this.variables = []
        console.log(locals)
        const loc = { label: 'locals', children: [] } as Tree
        for (const i of locals) {
          (loc.children as Tree[]).push({ label: i, children: [] })
        }
        const glob = { label: 'global', children: [] } as Tree
        for (const i of globals) {
          (glob.children as Tree[]).push({ label: i, children: [] })
        }
        this.variables.push(loc)
        this.variables.push(glob)
      })
  }

  getData () {
    axios.post(this.baseUrl + '/pdb/getfunc', { token: this.pdbSocket.id })
  }

  mounted () {
    this.initDebugger()
  }
}

</script>

<style scoped>
  @import 'xterm/css/xterm.css';

  #debugConsole {
    white-space: pre;
    text-align: left;
  }
  .continue {
    background-image: '@/asstes/logo.png';
  }
  .panel {
    display: block;
    height: 20px;
    width: 40px;
  }
</style>

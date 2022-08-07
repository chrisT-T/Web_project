<template>
  <div>
    <h1> {{ status }} </h1>
    <drag-box style="width: 100%; height: 100%">
      <drag-item class="TermContainer">
        <div id="debugTerm" @notify="handleResize"/>
      </drag-item>
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
  </div>
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
interface StackItem {
  func: string
  file: string
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
  stk = [] as StackItem[]
  stkStr = '' as string
  fitAddon = new FitAddon()
  variables = [] as Tree[]
  curline = 1 as number

  term = new Terminal({
    cursorBlink: true,
    macOptionIsMeta: true
  })

  socket = io('http://127.0.0.1:5000/pdb')

  pdbSocket = io()

  initDebugger () {
    this.term.open(document.getElementById('debugTerm') as HTMLElement)
    this.term.loadAddon(this.fitAddon)
    this.fitAddon.fit()
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
          console.log('Pdbsocket Connected')
        })
      })

      this.pdbSocket.on('pdb_quit', (data) => {
        this.status = data.flag
        this.pdbSocket.disconnect()
        this.socket.disconnect()
        this.variables = [] as Tree[]
        this.stk = [] as StackItem[]
      })

      this.pdbSocket.on('pdb_output', (data: {'consoleOutput': string, 'token': string}) => {
        console.log(data)
        if (data.token === this.pdbSocket.id) {
          this.consoleOutput += data.consoleOutput
          this.updateData()
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

  stop () {
    axios.post(this.baseUrl + '/pdb/runcmd', { token: this.pdbSocket.id, cmd: 'q' })
  }

  restart () {
    axios.post(this.baseUrl + '/pdb/runcmd', { token: this.pdbSocket.id, cmd: 'q' })
    // axios.post (this.baseUrl + '/pdb/debug', { token: this.pdbSocket.id, filepath: this.filePath })
    this.term.dispose()
    this.term = new Terminal({
      cursorBlink: true,
      macOptionIsMeta: true
    })
    this.socket = io('http://127.0.0.1:5000/pdb')
    setTimeout(() => {
      this.initDebugger()
    }, 2000)
  }

  updateData () {
    axios.post(this.baseUrl + '/pdb/curframe', { token: this.pdbSocket.id })
      .then((response) => {
        const rawLocals = JSON.parse(response.request.response).locals
        const rawGlobals = JSON.parse(response.request.response).globals
        const locals = rawLocals.split('\n')
        const globals = rawGlobals.split('\n')
        this.variables = []
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
        this.curline = JSON.parse(response.request.response).current_line
      })
    axios.post(this.baseUrl + '/pdb/getstack', { token: this.pdbSocket.id }).then(
      (response) => {
        const stklist = JSON.parse(response.request.response)
        // console.log(stklist)
        // for (let i = 1; i < stklist.length; i++) {
        // this.stk_file.push(stklist[i].match(/))
        // }
        this.stkStr = ''
        for (const i of stklist) {
          this.stkStr += i
        }
        this.stk = []
        for (let i = 1; i < stklist.length; i++) {
          const funct = stklist[i].match(/, code (\S*)>/)[1]
          let fil = stklist[i].match(/file '(\S*)'/)[1]
          if (/\//.test(fil)) {
            console.log('yes')
            fil = fil.match(/\/(\w*?).py/)[1] + '.py'
            console.log(fil)
          }
          this.stk.splice(0, 0, { func: funct, file: fil })
        }
      }
    )
  }

  test () {
    this.fitAddon.fit()
  }

  mounted () {
    this.initDebugger()
    const resize = document.getElementsByClassName('resize')
    for (const i of resize) {
      i.addEventListener('mouseup', this.test)
    }
  }
}

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

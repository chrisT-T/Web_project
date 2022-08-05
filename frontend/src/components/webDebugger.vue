<template>
  <div>
    <h1> {{ status }} </h1>
    <div id = "debugTerm"></div>
    <div id = "debugConsole">
      <p>{{ consoleOutput }}</p>
    </div>
    <button @click="getData"> n command </button>
    <button @click="setbreak"> b command </button>
    <input type="text" name="command" id="command" v-model="command">
    <button @click="send">send command </button>
  </div>
</template>

<script lang="ts">
import { Vue, prop } from 'vue-class-component'
import { Terminal } from 'xterm'
import io from 'socket.io-client'
import axios from 'axios'

class webDebuggerProps {
  debuggerName: string = prop({
    required: true
  })
}

export default class webDebugger extends Vue.with(webDebuggerProps) {
  baseUrl = 'http://127.0.0.1:' as string
  status = 'distanced' as string
  command = '' as string
  consoleOutput = '' as string

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
        axios.post(this.baseUrl + '/pdb/debug', { token: this.pdbSocket.id, filepath: './test_script/echo.py' }).then(() => {
          this.status = this.debuggerName
        })
      })

      this.pdbSocket.on('pdb_quit', (data) => {
        this.status = data.flag
        this.pdbSocket.disconnect()
        this.socket.disconnect()
      })

      this.pdbSocket.on('pdb_output', (data: {'consoleOutput': string, 'token': string}) => {
        console.log(data)
        if (data.token === this.pdbSocket.id) {
          this.consoleOutput += data.consoleOutput
        }
      })
    })

    this.socket.on('debugger_term_output', (data: {'output': string, 'token': string}) => {
      console.log(data)
      this.term.write(data.output)
    })
  }

  send () {
    axios.post(this.baseUrl + '/pdb/runcmd', { token: this.pdbSocket.id, cmd: this.command })
  }

  setbreak () {
    axios.post(this.baseUrl + '/pdb/runcmd', { token: this.pdbSocket.id, cmd: 'b 3' })
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
</style>

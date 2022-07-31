<template>
  <div>
    <h1> {{ status }} </h1>
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
  baseUrl = 'http://127.0.0.1:5000' as string
  status = 'distanced' as string
  command = '' as string
  consoleOutput = '' as string
  socket = io('http://127.0.0.1:5000/pdb', {
    auth: {
      token: this.debuggerName
    }
  })

  initDebugger () {
    this.socket.on('pdb-output', (data: {'consoleOutput': string, 'token': string}) => {
      console.log('rx')
      console.log(data)
      if (data.token === this.debuggerName) {
        console.log(data.consoleOutput)
        this.consoleOutput += data.consoleOutput
      }
    })

    this.socket.on('connect', () => {
      this.status = this.debuggerName
    })
  }

  send () {
    axios.post(this.baseUrl + '/pdb/runcmd', { token: this.debuggerName, cmd: this.command })
  }

  pdbN () {
    axios.post(this.baseUrl + '/pdbN', { token: this.debuggerName })
  }

  setbreak () {
    axios.post(this.baseUrl + '/pdb/runcmd', { token: this.debuggerName, cmd: 'b 3' })
  }

  getData () {
    axios.post(this.baseUrl + '/pdb/curframe', { token: this.debuggerName })
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

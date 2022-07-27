<template>
  <div>
    <h1> {{ status }} </h1>
    <div id="terminal"></div>
    <button id='runbtn' @click='runPython'> Run ./test.py in Terminal </button>
    <button id='runbtn' @click='runPdb'> Run ./test.py in Terminal (Debug mode) </button>
  </div>
</template>

<script lang="ts">
import { Vue, prop } from 'vue-class-component'
import { Terminal } from 'xterm'
import io from 'socket.io-client'
import axios from 'axios'

class webTerminalProps {
  termName: string = prop({
    required: true
  })
}

export default class webTerminal extends Vue.with(webTerminalProps) {
  term = new Terminal()
  status = 'disconnected'
  socket = io('http://127.0.0.1:5000/pty', {
    auth: {
      token: this.termName
    }
  })

  initTerminal () {
    this.term = new Terminal({
      cursorBlink: true,
      macOptionIsMeta: true
    })

    this.term.open(document.getElementById('terminal') as HTMLElement)

    this.term.writeln('This is the online terminal')

    this.term.onData((data) => {
      this.socket.emit('pty-input', { input: data, token: this.termName })
    })

    this.socket.on('pty-output', (data: {'output': string, 'token': string}) => {
      console.log(data.token)
      if (data.token === this.termName) {
        this.term.write(data.output)
      }
    })

    this.socket.on('connect', () => {
      this.status = this.termName
    })
  }

  runPython () {
    axios.post('http://127.0.0.1:5000/run', { token: this.termName, path: './test.py' })
  }

  runPdb () {
    axios.post('http://127.0.0.1:5000/runpdb', { token: this.termName, path: './test.py', breakPointList: [] })
  }

  mounted () {
    this.initTerminal()
  }
}
</script>

<style scoped>
  @import 'xterm/css/xterm.css';
</style>

<template>
  <div>
    <h1> {{ status }} </h1>
    <div id="terminal"></div>
    <div> <p> {{ pdbBuffer }} </p> </div>
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
  baseUrl = 'http://127.0.0.1:5000' as string
  term = new Terminal()
  status = 'disconnected'
  socket = io('http://127.0.0.1:5000/pty', {
    auth: {
      token: this.termName
    }
  })

  pdbBuffer = '' as string
  pdbFlag = '' as string

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
      if (data.token === this.termName) {
        this.term.write(data.output)
        if (this.pdbFlag !== '') {
          this.pdbBuffer += data.output
        }
      }
    })

    this.socket.on('connect', () => {
      this.status = this.termName
    })
  }

  mounted () {
    this.initTerminal()
  }
}
</script>

<style scoped>
  @import 'xterm/css/xterm.css';
</style>

<template>
  <div>
    <h1> {{ status }} </h1>
    <div id="terminal"></div>
  </div>
</template>

<script lang="ts">
import { Vue } from 'vue-class-component'
import { Terminal } from 'xterm'
import io from 'socket.io-client'

export default class webTerminal extends Vue {
  term = new Terminal()
  status = 'disconnected'
  socket = io('http://127.0.0.1:5000/pty')

  initTerminal () {
    this.term = new Terminal({
      cursorBlink: true,
      macOptionIsMeta: true
    })

    this.term.open(document.getElementById('terminal') as HTMLElement)

    this.term.writeln('This is the online terminal')

    this.term.onData((data) => {
      this.socket.emit('pty-input', { input: data })
    })

    this.socket.on('pty-output', (data: {'output': string}) => {
      this.term.write(data.output)
    })

    this.socket.on('connect', () => {
      this.status = 'connected'
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

<template>
  <div>
    <h1> {{ status }} </h1>
    <div id="debugger"> </div>
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
  status = 'distanced'
  term = new Terminal()
  socket = io('http://127.0.0.1:5000/pdb', {
    auth: {
      token: this.debuggerName
    }
  })

  initDebugger () {
    this.term = new Terminal({
      cursorBlink: true,
      macOptionIsMeta: true
    })

    this.term.open(document.getElementById('debugger') as HTMLElement)

    this.term.writeln('This is the debugger console')

    this.term.onData((data) => {
      console.log(data)
      this.socket.emit('pdb-input', { input: data, token: this.debuggerName })
      this.term.write(data)
    })

    this.socket.on('pdb-output', (data: {'consoleOutput': string, 'token': string}) => {
      console.log('rx')
      console.log(data)
      if (data.token === this.debuggerName) {
        console.log(data.consoleOutput)
        this.term.write(data.consoleOutput)
      }
    })

    this.socket.on('connect', () => {
      this.status = this.debuggerName
    })
  }

  mounted () {
    this.initDebugger()
  }
}

</script>

<style scoped>
  @import 'xterm/css/xterm.css';
</style>

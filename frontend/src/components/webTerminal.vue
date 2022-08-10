<template>
  <div>
    <h1> {{ status }} </h1>
    <div id="terminal"></div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { Terminal } from 'xterm'
import io from 'socket.io-client'

const props = defineProps<{
  termName: string
}>()

let baseUrl = 'http://127.0.0.1:5000' as string
let term = new Terminal()
let status = 'disconnected'
let socket = io('/api/pty', {
  auth: {
    token: props.termName
  }
})


function initTerminal () {
  term = new Terminal({
    cursorBlink: true,
    macOptionIsMeta: true
  })

  term.open(document.getElementById('terminal') as HTMLElement)

  term.writeln('This is the online terminal')

  term.onData((data) => {
    socket.emit('pty-input', { input: data, token: props.termName })
  })

  socket.on('pty-output', (data: {'output': string, 'token': string}) => {
    if (data.token === props.termName) {
      term.write(data.output)
    }
  })

  socket.on('connect', () => {
    status = props.termName
  })
}

onMounted(() => {
  initTerminal()
})
</script>

<style scoped>
  @import 'xterm/css/xterm.css';
</style>

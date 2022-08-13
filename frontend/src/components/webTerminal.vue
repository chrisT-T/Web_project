<template>
  <div ref="termDiv"></div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { Terminal } from 'xterm'
import io from 'socket.io-client'

const baseUrl = 'http://127.0.0.1:5000' as string
const termDiv = ref<HTMLDivElement>()
let term = new Terminal()
const status = ref<string>('disconnected')
const socket = io('http://127.0.0.1:5000/pty')

function initTerminal () {
  term = new Terminal({
    cursorBlink: true,
    macOptionIsMeta: true
  })

  term.open(termDiv.value)

  term.writeln('This is the online terminal')

  term.onData((data) => {
    socket.emit('pty-input', { input: data, token: socket.id })
  })

  socket.on('pty-output', (data: {'output': string, 'token': string}) => {
    if (data.token === socket.id) {
      term.write(data.output)
    }
  })

  socket.on('connect', () => {
    status.value = socket.id
  })
}

onMounted(() => {
  initTerminal()
})
</script>

<style scoped>
  /* @import 'xterm/css/xterm.css'; */
</style>

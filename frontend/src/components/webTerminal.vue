<template>
  <div v-loading="loading" ref="termDiv"></div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Terminal } from 'xterm'
import io from 'socket.io-client'

const termDiv = ref<HTMLDivElement>()
let term = new Terminal()
const status = ref<string>('disconnected')
const socket = io('/pty')
const loading = ref(true)

function initTerminal () {
  term = new Terminal({
    cursorBlink: true,
    macOptionIsMeta: true
  })

  term.open(termDiv?.value as HTMLElement)

  term.onData((data) => {
    socket.emit('pty-input', { input: data, token: socket.id })
  })

  socket.on('pty-output', (data: {'output': string, 'token': string}) => {
    loading.value = false
    term.write(data.output)
  })

  socket.on('connect', () => {
    status.value = socket.id
  })
}

onMounted(() => {
  initTerminal()
})

onUnmounted(() => {
  socket.disconnect()
})
</script>

<style scoped>
  /* @import 'xterm/css/xterm.css'; */
</style>

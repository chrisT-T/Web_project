<template>
  <div ref="debugTerm"/>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { Terminal } from 'xterm'
import io from 'socket.io-client'
import { FitAddon } from 'xterm-addon-fit'

const socket = io('http://127.0.0.1:5000/pdb')
const fitAddon = new FitAddon()
const debugTerm = ref<HTMLDivElement>()
const term = new Terminal({
  cursorBlink: true,
  macOptionIsMeta: true
})
let port = 0 as number
const emit = defineEmits <{(e: 'getPdbPort', port: number): void}>()

function init () {
  console.log('msg from debugger Terminal')
  term.open(debugTerm.value)
  term.loadAddon(fitAddon)
  fitAddon.fit()
  term.writeln('Debugger Terminal\n')
  term.onData((data) => {
    console.log(data)
    socket.emit('debugger_term_input', { input: data, token: socket.id })
  })

  socket.on('debugger_port', (data: {'port': number, 'token': string}) => {
    console.log('debugger terminal get the port' + data)
    port = data.port
    emit('getPdbPort', data.port)
  })

  socket.on('debugger_term_output', (data: {'output': string, 'token': string}) => {
    term.write(data.output)
  })

  socket.on('disconnect', () => {
    console.log('port ' + port + ' disconnected')
  })
}

onMounted(() => {
  init()
})

</script>

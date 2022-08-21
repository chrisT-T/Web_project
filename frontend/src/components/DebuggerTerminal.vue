<template>
  <div ref="debugTerm"/>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { Terminal } from 'xterm'
import io from 'socket.io-client'
import { FitAddon } from 'xterm-addon-fit'

const socket = io('/pdb') // 这里是 connect 到 pdb 的 socket
const fitAddon = new FitAddon()
const debugTerm = ref<HTMLDivElement>()
const term = new Terminal({
  cursorBlink: true,
  macOptionIsMeta: true
})
let port = 0 as number
// 发送端口 / 启动按钮
// 这里格式是eslint 规定
const emit = defineEmits<{(e: 'getPdbPort', port: number): void
  (e: 'disconnect'): void
}>()

function init () {
  console.log('msg from debugger Terminal')
  term.open(debugTerm.value as HTMLDivElement)
  term.loadAddon(fitAddon)
  fitAddon.fit()
  term.writeln('Debugger Terminal\n')
  term.onData((data) => {
    console.log(data)
    socket.emit('debugger_term_input', { input: data, token: socket.id })
  })

  socket.on('debugger_port_allocated', (data: {'port': number, 'token': string}) => {
    port = data.port
    emit('getPdbPort', data.port)
  })

  socket.on('debugger_term_output', (data: {'output': string, 'token': string}) => {
    term.write(data.output)
  })

  socket.on('disconnect', () => {
    console.log('port ' + port + ' disconnected')
    emit('disconnect')
  })

  socket.on('clear_screen', () => {
    term.clear()
  })
}

onMounted(() => {
  init()
})

</script>

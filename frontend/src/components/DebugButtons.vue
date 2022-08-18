<template>
<div style="display: flex; flex:1;height: ;">
  <el-icon @click="cont" title="Continue" :size="size"><CaretRight /></el-icon>
  <el-icon @click="next" title="Step Over" :size="size"><Right /></el-icon>
  <el-icon @click="stepInto" title="Step Into" :size="size"><Download /></el-icon>
  <el-icon @click="stepOut" title="Step Out" :size="size"><Upload /></el-icon>
  <el-icon @click="restart" title="Restart" :size="size"><RefreshLeft /></el-icon>
  <el-icon @click="stop" title="Stop" :size="size"><CloseBold /></el-icon>
</div>
</template>
<script lang="ts" setup>
import axios from 'axios'
let __baseUrl = ''
let __token = ''
let mPort = 0
const size = 40 as number

// eslint-disable-next-line func-call-spacing
const emit = defineEmits <{
  (e: 'runcmdWithBreakPoint', cmd: string): void,
  (e: 'restartDebugger', port: number): void
}>()

function init (port: number, token: string) {
  mPort = port
  __baseUrl = 'http://127.0.0.1:' + port.toString()
  __token = token
  console.log('buttons prepared with port: ' + port + ' token: ' + token)
}

function runcmd (cmd: string, bps: Map<string, number[]>, userPath: string) {
  axios.post(__baseUrl + '/pdb/clearBreakPoint', { token: __token }).then(() => {
    const tmp = []
    bps.forEach((value, key) => {
      value.forEach((lineno) => {
        console.log(key, lineno, `b ${userPath}/${key}: ${lineno}`)
        tmp.push(
          axios.post(__baseUrl + '/pdb/runcmd', { token: __token, cmd: `b ${userPath}/${key}: ${lineno}` })
        )
      })
    })
    axios.all(tmp).then(() => {
      axios.post(__baseUrl + '/pdb/runcmd', { token: __token, cmd })
    })
  })
}

function cont () {
  emit('runcmdWithBreakPoint', 'c')
}

function next () {
  emit('runcmdWithBreakPoint', 'c')
}

function stepInto () {
  emit('runcmdWithBreakPoint', 's')
  console.log('step into')
}

function stepOut () {
  emit('runcmdWithBreakPoint', 'u')
}

function stop () {
  emit('runcmdWithBreakPoint', 'q')
}

function restart () {
  axios.post(__baseUrl + '/pdb/runcmd', { token: __token, cmd: 'q' }).then((response) => {
    console.log(response)
    emit('restartDebugger', mPort)
  })
}
defineExpose({
  init,
  runcmd
})
</script>
<style scoped>

</style>

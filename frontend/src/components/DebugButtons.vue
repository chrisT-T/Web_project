<template>
<div style="display: flex;">
  <el-icon @click="cont" title="Continue" :size="size"><CaretRight /></el-icon>
  <el-icon @click="next" title="Step Over" :size="size"><Right /></el-icon>
  <el-icon @click="stepInto" title="Step Into" :size="size"><Download /></el-icon>
  <el-icon @click="stepOut" title="Step Out" :size="size"><Upload /></el-icon>
  <el-icon @click="restart" title="Restart" :size="size"><RefreshLeft /></el-icon>
  <el-icon @click="stop" title="Stop" :size="size"><CloseBold /></el-icon>
</div>
</template>
<script lang="ts" setup>
import { getCurrentInstance } from 'vue'
import axios from 'axios'
let __baseUrl = ''
let __token = ''
const size = 40 as number

const emit = defineEmits<{(e: 'runcmdWithBreakPoint', cmd: string): void}>()

function init (port: number, token: string) {
  __baseUrl = 'http://127.0.0.1:' + port.toString()
  __token = token
  console.log('buttons prepared with port: ' + port + ' token: ' + token)
}

function runcmd (cmd: string, bps: Map<string, number[]>, userPath: string) {
  axios.post(__baseUrl + '/pdb/clearBreakPoint', { token: __token }).then(() => {
    bps.forEach((value, key) => {
      value.forEach((lineno) => {
        console.log(key, lineno, `b ${userPath}/${key}: ${lineno}`)
        axios.post(__baseUrl + '/pdb/runcmd', { token: __token, cmd: `b ${userPath}/${key}: ${lineno}` })
      })
    })
    axios.post(__baseUrl + '/pdb/runcmd', { token: __token, cmd })
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
  emit('runcmdWithBreakPoint', 'q')
}
defineExpose({
  init,
  runcmd
})
</script>
<style scoped>

</style>

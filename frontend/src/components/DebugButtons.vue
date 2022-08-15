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
import axios from 'axios'
let __baseUrl = ''
let __token = ''
const size = 40 as number

function init (port: number, token: string) {
  __baseUrl = 'http://127.0.0.1:' + port.toString()
  __token = token
  console.log('buttons prepared with port: ' + port + ' token: ' + token)
}
function cont () {
  axios.post(__baseUrl + '/pdb/runcmd', { token: __token, cmd: 'c' })
}

function next () {
  axios.post(__baseUrl + '/pdb/runcmd', { token: __token, cmd: 'n' })
}

function stepInto () {
  axios.post(__baseUrl + '/pdb/runcmd', { token: __token, cmd: 's' })
  console.log('step into')
}

function stepOut () {
  axios.post(__baseUrl + '/pdb/runcmd', { token: __token, cmd: 'u' })
}

function stop () {
  axios.post(__baseUrl + '/pdb/runcmd', { token: __token, cmd: 'q' })
}

function restart () {
  axios.post(__baseUrl + '/pdb/runcmd', { token: __token, cmd: 'q' })
}
defineExpose({
  init
})
</script>
<style scoped>

</style>

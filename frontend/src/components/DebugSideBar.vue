<template>
<splitpanes horizontal>
  <pane min-size="20">
    <p class="heading">VARIABLES <span class="buttons"><el-icon title="Collapse All" :size="iconSize" class="is-loading"><Remove /></el-icon></span></p>
    <el-tree :default-expand-all="true" :data="variables" style="height:100%" :props="{
      label: 'label',
      children: 'children',
    }"></el-tree>
  </pane>
  <pane min-size="20">
    <p class="heading">WATCH
      <span class="buttons">
        <el-icon title="Add Expression" :size="iconSize"><CirclePlus /></el-icon>
        <el-icon title="Remove All Expresions" :size="iconSize" :class="watchAvailable"><CircleClose /></el-icon>
        <el-icon title="Collapse All" :size="iconSize" :class="watchAvailable"><Remove /></el-icon>
      </span>
    </p>
  </pane>
  <pane min-size="20">
    <p class="heading">CALL STACK </p>
    <div v-for="(item,index) in stk" :key="index">
      <span class="stkFunc">{{item.func}}</span><span class="stkFile">{{item.file}}</span><br>
    </div>
  </pane>
</splitpanes>
</template>

<script lang="ts" setup>

import { ref } from 'vue'
import { Splitpanes, Pane } from 'splitpanes'
import axios from 'axios'

interface Tree {
  label: string
  children?: Tree[]
}

interface StackItem {
  func: string
  file: string
}

const props = defineProps({
  token: String
})

const baseUrl = 'http://127.0.0.1:' as string
const variables = ref<Tree[]>([{ label: 'locals', children: [] }, { label: 'global', children: [] }])
const stk = ref<StackItem[]>([])
const iconSize = 20
let watchAvailable = 'disabled'
function updateData () {
  axios.post(baseUrl + '/pdb/curframe', { token: props.token })
    .then((response) => {
      const rawLocals = JSON.parse(response.request.response).locals
      const rawGlobals = JSON.parse(response.request.response).globals
      const locals = rawLocals.split('\n')
      const globals = rawGlobals.split('\n')
      variables.value = []
      const loc = { label: 'locals', children: [] } as Tree
      for (const i of locals) {
        (loc.children as Tree[]).push({ label: i, children: [] })
      }
      const glob = { label: 'global', children: [] } as Tree
      for (const i of globals) {
        (glob.children as Tree[]).push({ label: i, children: [] })
      }
      variables.value.push(loc)
      variables.value.push(glob)
    })
  axios.post(baseUrl + '/pdb/getstack', { token: props.token }).then(
    (response) => {
      const stklist = JSON.parse(response.request.response)
      stk.value = []
      for (let i = 1; i < stklist.length; i++) {
        const funct = stklist[i].match(/, code (\S*)>/)[1]
        let fil = stklist[i].match(/file '(\S*)'/)[1]
        if (/\//.test(fil)) {
          console.log('yes')
          fil = fil.match(/\/(\w*?).py/)[1] + '.py'
          console.log(fil)
        }
        stk.value.splice(0, 0, { func: funct, file: fil })
      }
    }
  )
  watchAvailable = ''
}
</script>

<style scoped>
* {
  font-family:'Courier New', Courier, monospace
}
.heading {
  text-align: left;
  font-size: 15px;
  margin: 2px;
  padding: 6px 2px 2px;
}

.buttons {
  float:right;
  margin:-3px 0 0;
}
.splitpanes .splitpanes__splitter{
  background-color: black;
}
:deep(.el-tree) {
  background-color: var(--el-color-primary-light-8);;
}
.disabled {
  color: rgb(192, 192, 192)
}
</style>

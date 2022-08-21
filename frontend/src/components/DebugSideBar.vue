<template>
<splitpanes horizontal>
  <pane min-size="20" style="overflow-y:scroll; overflow-x:hidden">
    <p class="heading">VARIABLES
      <span class="buttons">
        <el-icon title="Collapse All" :size="iconSize" @click="collapseVar"><Remove /></el-icon>
      </span>
    </p>
    <el-tree :default-expand-all="true" :data="variables" ref="varTree">
      <template #default="{ node, data }">
        <span class="tree-node">
          <span class="var_data">{{node.data.data}}</span>: &nbsp;<span class="var_value"> {{data.value}}</span>
        </span>
      </template>
    </el-tree>
  </pane>
  <pane min-size="20">
    <p class="heading">WATCH
      <span class="buttons">
        <el-icon title="Add Expression" :size="iconSize" @click="addExpression"><CirclePlus /></el-icon>
        <el-icon title="Remove All Expresions" :size="iconSize" :class="watchAvailable" @click="clearWatch"><CircleClose /></el-icon>
        <el-icon title="Collapse All" :size="iconSize" :class="watchAvailable"><Remove /></el-icon>
      </span>
    </p>
    <el-tree :default-expand-all="true" :data="watchData" :key="watchData">
      <template #default="{ node, data }">
        <span class="tree-node">
          <span class="var_data">{{node.data.data}}</span>: &nbsp;<span class="var_value"> {{node.data.value}}</span>
          <el-icon style="position: absolute;right: 0;" @click="remove(node, data)"><Close /></el-icon>
        </span>
      </template>
    </el-tree>
    <el-input placeholder="Expression to watch"  v-model="watchToBeAdded" @blur="closeInput" @keyup.enter="addWatch" ref="watchInput" v-if="addingWatch"></el-input>
  </pane>
  <pane min-size="20">
    <p class="heading">CALL STACK </p>
    <div v-for="(item, index) in stk" :key="index">
      <span style="float: left">{{item.func}}</span><span style="float: right">{{item.file}}</span><br>
    </div>
  </pane>
</splitpanes>
</template>

<script lang="ts" setup>

import { ref, nextTick, h } from 'vue'
import { Splitpanes, Pane } from 'splitpanes'
import axios from 'axios'
import { ElNotification } from 'element-plus'

interface Tree {
  id: number
  isRoot: boolean
  data: string
  value: string
  children?: Tree[]
}

interface StackItem {
  func: string
  file: string
}

// eslint-disable-next-line func-call-spacing
const emit = defineEmits<{
  (e: 'updateFocusLine', lineno: number, file: string): void
}>()

const variables = ref<Tree[]>([
  { id: 0, data: 'Locals', value: '', isRoot: true, children: [] },
  { id: 1, data: 'Globals', value: '', isRoot: true, children: [] }
])
const varTree = ref()
function collapseVar () {
  for (const node of varTree.value.store.nodesMap) {
    node.expanded = false
  }
}
const stk = ref<StackItem[]>([])
const iconSize = 20
const watchAvailable = ref<string>('disabledButton')

let mPort = 0
let mToken = ''

function updateData (port: number, token: string) {
  mPort = port
  mToken = token
  console.log('update date in side bar /pdb/curframe')
  // update the variables
  axios.post('/pdb/curframe', { token, port })
    .then((response) => {
      try {
        let id = 2
        console.log(JSON.parse(response.request.response))
        const rawLocals = JSON.parse(response.request.response).locals as string
        const rawGlobals = JSON.parse(response.request.response).globals as string
        const locals = rawLocals.split('\n')
        console.log(locals)
        const globals = rawGlobals.split('\n')
        variables.value = [
          { id: 0, data: 'Locals', value: '', isRoot: true, children: [] },
          { id: 1, data: 'Globals', value: '', isRoot: true, children: [] }
        ]
        if (locals[0] !== '') {
          for (const i of locals) {
            const dat = i.split('=')[0]
            const val = i.split('=')[1]
            variables.value[0].children?.push({ id: id++, data: dat, value: val, isRoot: false, children: [] })
          }
        }
        if (globals[0] !== '') {
          for (const i of globals) {
            const dat = i.split('=')[0]
            const val = i.split('=')[1]
            variables.value[1].children?.push({ id: id++, data: dat, value: val, isRoot: false, children: [] })
          }
        }
        const currentLine = JSON.parse(response.request.response).current_line as number
        const rawpath = JSON.parse(response.request.response).rawfilename as string
        emit('updateFocusLine', currentLine, rawpath)
      } catch (e: TypeError) {
        console.log(e)
        variables.value = []
      } finally {
        console.log('finally')
      }
    })
  // update the call stack
  axios.post('/pdb/getstack', { port, token }).then(
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
  if (watchList.value.length === 0) {
    watchAvailable.value = 'disabledButton'
  } else {
    updateWatch()
    watchAvailable.value = 'availableButton'
  }
}

const watchList = ref<string[]>([])
const watchData = ref<Tree[]>([])
const watchInput = ref()
const watchToBeAdded = ref('')
const addingWatch = ref<boolean>(false)

function updateWatch () {
  const tmp = watchList.value.map(element => { return axios.post('/pdb/repr', { port: mPort, token: mToken, repr: element }) })
  axios.all(tmp).then((resp) => {
    watchData.value.splice(0)
    resp.forEach((respitem, index) => {
      console.log(respitem, respitem.data)
      const flag = JSON.parse(respitem.request.response).runflag as boolean
      if (flag === true) {
        const value = JSON.parse(respitem.request.response).value
        watchData.value.push({
          id: index,
          isRoot: false,
          data: watchList.value[index],
          value,
          children: []
        } as Tree)
      } else {
        watchData.value.push({
          id: index,
          isRoot: false,
          data: watchList.value[index],
          value: '',
          children: []
        } as Tree)
      }
    })
  })
}

defineExpose({
  updateData,
  endDebug
})
// close addwatch input
function closeInput () {
  addingWatch.value = false
  watchInput.value.clear()
}
// add addwatch input value into watch
function addWatch (e) {
  watchList.value.push(e.target.value)
  ElNotification({
    title: 'Debugger: Watch',
    message: h('i', { style: 'color: teal' }, `Add a new watch expression ${e.target.value}`)
  })
  watchAvailable.value = 'availableButton'
  updateWatch()
  closeInput()
}
// show addwatch input
async function addExpression () {
  addingWatch.value = true
  await nextTick()
  watchInput.value.focus()
}
function clearWatch () {
  watchList.value = []
  watchData.value = []
  watchAvailable.value = 'disabledButton'
}

function remove (node: Node, data: Tree) {
  const parent = node.parent
  const children: Tree[] = parent.data.children || parent.data
  const index = children.findIndex((d) => d.id === data.id)
  children.splice(index, 1)
  watchData.value = [...watchData.value]
  const listidx = watchList.value.findIndex((d) => d === data.data)
  watchList.value.splice(listidx, 1)
  console.log(watchList.value)
}

function endDebug () {
  stk.value = []
  variables.value = [
    { id: 0, data: 'Locals', value: '', isRoot: true, children: [] },
    { id: 1, data: 'Globals', value: '', isRoot: true, children: [] }
  ]
  clearWatch()
}

</script>

<style scoped>
* {
  font-family:Arial, Helvetica, sans-serif;
  font-size: 14px;
}
.heading {
  text-align: left;
  font-size: 14px;
  margin: 0;
  padding: 6px 2px 2px;
  justify-content: center;
}

.buttons {
  float:inline-end;
  margin:-3px 0 0;
}
:deep(.splitpanes__splitter){
  height: 2px;
  background-color: var(--el-border-color-light);
}
:deep(.el-tree-node__content) {
  width: 100%;
}
:deep(.el-tabs__nav-wrap.is-left::after) {
  background-color: brown;
  width: 20px;
}
.disabledButton {
  color: rgb(192, 192, 192)
}
.availableButton {
  color: black
}
:deep(.el-tabs__content) {
  width: 100%;
}
:deep(.el-tree__empty-block) {
  display: none;
}
.tree-node {
  flex: 1;
  display: flex;
  padding-right: 8px;
  width: 80%;
  text-align: left;
}
:deep(.is-leaf) {
  /* display: none; */
}
.var_data {
  color: blueviolet;
  text-overflow: ellipsis;
  overflow: hidden;
  width: auto;
  white-space: nowrap;
}
.var_value {
  color: green;
  text-overflow: ellipsis;
  overflow: hidden;
  width: auto;
  white-space: nowrap;
}
</style>

<template>
<splitpanes horizontal>
  <pane min-size="20" style="overflow-y:scroll; overflow-x:hidden">
    <p class="heading">VARIABLES
      <span class="buttons">
        <el-icon title="Collapse All" :size="iconSize"><Remove /></el-icon>
      </span>
    </p>
    <p style="width:100%; margin: 5px 0px 0px 10px; text-align: left; color: grey">Locals </p>
    <el-tree :default-expand-all="true" :data="locVar">
      <template #default="{ node, data }">
        <span class="tree-node">
          <span class="var_data">{{node.data.data}}</span>: &nbsp;<span class="var_value"> {{data.value}}</span>
        </span>
      </template>
    </el-tree>
    <p style="width:100%; margin: 5px 0px 0px 10px; text-align: left; color: grey">Globals </p>
    <el-tree :default-expand-all="true" :data="globVar">
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
          <el-icon style="float:right" @click="remove(node, data)"><Close /></el-icon>
        </span>
      </template>
    </el-tree>
    <el-input placeholder="Expression to watch"  v-model="watchToBeAdded" @blur="closeInput" @keyup.enter="addWatch" ref="watchInput" v-if="addingWatch"></el-input>
  </pane>
  <pane min-size="20">
    <p class="heading">CALL STACK </p>
    <div v-for="(item,index) in stk" :key="index">
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

const locVar = ref<Tree[]>([])
const globVar = ref<Tree[]>([])
const stk = ref<StackItem[]>([])
const watchList = ref<string[]>([])
const watchData = ref<Tree[]>([])
const watchInput = ref()
const watchToBeAdded = ref('')
const addingWatch = ref<boolean>(false)
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
        let locid = 1
        let globid = 1
        console.log(JSON.parse(response.request.response))
        const rawLocals = JSON.parse(response.request.response).locals as string
        const rawGlobals = JSON.parse(response.request.response).globals as string
        const locals = rawLocals.split('\n')
        const globals = rawGlobals.split('\n')
        locVar.value = []
        globVar.value = []
        for (const i of locals) {
          const dat = i.split('=')[0]
          const val = i.split('=')[1]
          locVar.value.push({ id: locid++, data: dat, value: val, children: [] })
        }
        for (const i of globals) {
          const dat = i.split('=')[0]
          const val = i.split('=')[1]
          globVar.value.push({ id: globid++, data: dat, value: val, children: [] })
        }
        const currentLine = JSON.parse(response.request.response).current_line as number
        const rawpath = JSON.parse(response.request.response).rawfilename as string
        emit('updateFocusLine', currentLine, rawpath)
      } catch (e: TypeError) {
        console.log(e)
        locVar.value = []
        globVar.value = []
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
          data: watchList.value[index],
          value,
          children: []
        } as Tree)
      } else {
        watchData.value.push({
          id: index,
          data: watchList.value[index],
          value: '',
          children: []
        } as Tree)
      }
    })
  })
}

defineExpose({
  updateData
})

function closeInput () {
  addingWatch.value = false
}
// 添加 watch 对象
function addWatch (e) {
  watchList.value.push(e.target.value)
  ElNotification({
    title: 'Debugger: Watch',
    message: h('i', { style: 'color: teal' }, `Add a new watch expression ${e.target.value}`)
  })
  e.target.value = ''
  updateWatch()
  closeInput()
}
// 显示添加 watch 对象的框
async function addExpression () {
  addingWatch.value = true
  await nextTick()
  watchInput.value.focus()
}
// 清空 watch
function clearWatch () {
  watchList.value = []
  watchData.value = []
}
function remove (node: Node, data: Tree) {
  const parent = node.parent
  const children: Tree[] = parent.data.children || parent.data
  const index = children.findIndex((d) => d.id === data.id)
  children.splice(index, 1)
  dataSource.value = [...dataSource.value]
}
</script>

<style scoped>
.heading {
  text-align: left;
  font-size: 15px;
  margin: 2px;
  padding: 6px 2px 2px;
}

.buttons {
  float:inline-end;
  margin:-3px 0 0;
}
:deep(.splitpanes__splitter){
  background-color: var(--el-color-primary-dark-2);
  height: 3px;
}
:deep(.el-tree) {
  background-color: var(--el-color-primary-light-8);
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
}
.var_value {
  color: green;
  text-overflow: ellipsis;
  overflow: hidden;
  width: auto;
  white-space: nowrap;
}
</style>

<template>
<splitpanes horizontal>
  <pane>
    <div class="variables"  >
      <p class="heading" >VARIABLES <span class="buttons"><el-icon><Remove /></el-icon></span></p>
      <el-tree :default-expand-all="true" :data="variables" style="height:100%" :props="{
        label: 'label',
        children: 'children',
      }"></el-tree>
    </div>
  </pane>
  <pane>
    <div class="watch">
      <p class="heading" >WATCH
        <span class="buttons">
          <el-icon title="Add Expression"><CirclePlus /></el-icon>
          <el-icon title="Remove All Expresions"><CircleClose /></el-icon>
          <el-icon><Remove /></el-icon>
        </span>
      </p>
    </div>
  </pane>
</splitpanes>
</template>

<script lang="ts" setup>

import { ref, onMounted } from 'vue'
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

function updateData (port: number, token: string) {
  console.log('update date in side bar ' + port, baseUrl + port.toString() + '/pdb/curframe')
  axios.post(baseUrl + port.toString() + '/pdb/curframe', { token })
    .then((response) => {
      try {
        console.log(JSON.parse(response.request.response))
        const rawLocals = JSON.parse(response.request.response).locals as string
        const rawGlobals = JSON.parse(response.request.response).globals as string
        const locals = rawLocals.split('\n')
        const globals = rawGlobals.split('\n')
        variables.value = []
        const loc = { label: 'locals', children: [] } as Tree
        const glob = { label: 'global', children: [] } as Tree
        for (const i of locals) {
          (loc.children as Tree[]).push({ label: i, children: [] })
        }
        for (const i of globals) {
          (glob.children as Tree[]).push({ label: i, children: [] })
        }
        variables.value.push(loc)
        variables.value.push(glob)
      } catch (e: TypeError) {
        console.log(e)
        variables.value = []
        const loc = { label: 'locals', children: [] } as Tree
        const glob = { label: 'global', children: [] } as Tree
        variables.value.push(loc)
        variables.value.push(glob)
      } finally {
        console.log('finally')
      }
    })
  axios.post(baseUrl + port.toString() + '/pdb/getstack', { token }).then(
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
}

defineExpose({
  updateData
})
</script>

<style scoped>
.heading {
  text-align: left;
}

.buttons {
  float:right;
}

</style>

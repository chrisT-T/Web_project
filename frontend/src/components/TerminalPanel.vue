<template>
  <div>
    <el-tabs v-model="editableTabsValue" type="card" editable class="demo-tabs" @edit="handleTabsEdit" tab-position="top" strech>
      <el-tab-pane v-for="item in editableTabs" :key="item.name" :label="item.title" :name="item.name">
      <component :is=item.content v-bind="$attrs"></component>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script lang="ts" setup>
import { ref, markRaw } from 'vue'
import webTerminal from './webTerminal.vue'
import DebuggerTerminal from './DebuggerTerminal.vue'
let tabIndex = 2
const editableTabsValue = ref('1')
const editableTabs = ref([])

const handleTabsEdit = (targetName: string, action: 'remove' | 'add') => {
  if (action === 'add') {
    const newTabName = `${++tabIndex}`
    editableTabs.value.push({
      title: 'Terminal',
      name: newTabName,
      content: markRaw(webTerminal)
    })
    editableTabsValue.value = newTabName
  } else if (action === 'remove') {
    const tabs = editableTabs.value
    let activeName = editableTabsValue.value
    if (activeName === targetName) {
      tabs.forEach((tab, index) => {
        if (tab.name === targetName) {
          const nextTab = tabs[index + 1] || tabs[index - 1]
          if (nextTab) {
            activeName = nextTab.name
          }
        }
      })
    }

    editableTabsValue.value = activeName
    editableTabs.value = tabs.filter((tab) => tab.name !== targetName)
  }
}

function startDebuggerTerminal () {
  const newTabName = `${++tabIndex}`
  editableTabs.value.push({
    title: 'Py Debugger',
    name: newTabName,
    content: markRaw(DebuggerTerminal)
  })
  editableTabsValue.value = newTabName
}

defineExpose({
  startDebuggerTerminal
})
</script>

<style scope>
</style>

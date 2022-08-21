<template>
  <div class="variable_table">
    <p class="heading" >Variables:</p>
    <el-tree :default-expand-all="true" :data="data" :props="{
      label: 'label',
      children: 'children',
    }"></el-tree>
  </div>
</template>

<script lang="ts" setup>

import { onMounted } from 'vue'

const props = defineProps({
  data: Object
})
</script>

<style scoped>
.variable_table {
  display: block;
  width: 200px;
  height: 400px;
}
.heading{
  text-align: left;
  font-size: 20px;
  font-weight: bold;
}
:deep(.el-tree__empty-text) {
  color: white;
}
</style>

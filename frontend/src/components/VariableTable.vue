<template>
  <div class="variable_table">
    <p class="heading"> &nbsp; &nbsp; &nbsp;Variables:</p>
    <el-tree :data="data" :props="{
      label: 'label',
      children: 'children',
    }"></el-tree>
  </div>
</template>

<script lang="ts">

import { Vue, Options } from 'vue-class-component'

interface Tree {
  label: string
  children?: Tree[]
}

@Options({
  props: {
    data: Object
  }
})

export default class VariableTable extends Vue {
  mounted () {
    console.log(this.data)
  }
}
</script>

<style scoped>
.variable_table {
  display: block;
  width: 200px;
  height: 400px;
}
.heading{
  text-align: left;
}
</style>

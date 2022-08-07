<template>
  <div class="variable_table">
    <el-tree :data="dat" :props="{
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
    console.log(this.dat)
  }

  dat: Tree[] = [
    {
      label: '标签1',
      children: [
        {
          label: '标签1-1'
        },
        {
          label: '标签1-2'
        }
      ]
    },
    {
      label: '标签2',
      children: [
        {
          label: '标签2-1',
          children: [
            {
              label: '标签2-1-1'
            },
            {
              label: '标签2-1-2'
            }
          ]
        }
      ]
    }
  ]
}
</script>

<style scoped>
.variable_table {
  display: block;
  width: 200px;
  height: 400px;
}
</style>

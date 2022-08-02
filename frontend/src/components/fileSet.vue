<template>
<div>
  <el-tree :data="data" :props="defaultProps" @node-click="handleNodeClick" />
</div>
</template>

<script lang="ts" setup>
interface Tree {
  label: string
  children?: Tree[]
}

const handleNodeClick = (data: Tree) => {
  console.log(data)
  if (data.children === undefined) {
    console.log('is leaf')
  }
}

const data: Tree[] = [
  {
    label: 'Level one 1',
    children: [
      {
        label: 'Level two 1-1',
        children: [
          {
            label: 'Level three 1-1-1'
          }
        ]
      }
    ]
  },
  {
    label: 'Level one 2',
    children: [
      {
        label: 'Level two 2-1',
        children: [
          {
            label: 'Level three 2-1-1',
            children: [
              {
                label: 'Level four 2-1-1-1',
                children: [
                  {
                    label: 'Level five 2-1-1-1-1'
                  }
                ]
              }
            ]
          }
        ]
      },
      {
        label: 'Level two 2-2',
        children: [
          {
            label: 'Level three 2-2-1'
          }
        ]
      }
    ]
  },
  {
    label: 'Level one 3',
    children: [
      {
        label: 'Level two 3-1',
        children: [
          {
            label: 'Level three 3-1-1'
          }
        ]
      },
      {
        label: 'Level two 3-2',
        children: [
          {
            label: 'Level three 3-2-1'
          }
        ]
      }
    ]
  }
]

const defaultProps = {
  children: 'children',
  label: 'label'
}
</script>

<style scoped>
:deep(.el-tree-node__content) {
  display: flex;
  width: 100%;
  height: max-content;
}
:deep(.el-tree) {
  height: 100%;
  width: 100%;
  background-color: transparent;
}
</style>

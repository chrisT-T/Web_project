<template>
  <div class="common-layout">
    <el-header>
      Header
    </el-header>
    <el-main>
      <el-button :icon="Folder" class="close-btn" @click="showFolder();" circle />
      <div id="fileManager" v-bind:style="{width: showPage.detailWidth + 'px'}">
        <el-tree :data="data" :props="defaultProps" @node-click="handleNodeClick" />
      </div>
      <div id="codingArea">Coding area</div>
    </el-main>
    <el-footer>Footer</el-footer>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, reactive } from 'vue'
import {
  Folder
} from '@element-plus/icons-vue'

interface Tree {
  label: string
  children?: Tree[]
}

const handleNodeClick = (data: Tree) => {
  console.log(data)
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
      },
      {
        label: 'Level two 2-1',
        children: [
          {
            label: 'Level three 2-1-1'
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
      }
    ]
  }
]

const defaultProps = {
  children: 'children',
  label: 'label'
}

const showFolder = () => {
  if (showPage.detailWidth === 0) {
    showPage.detailWidth = 200
  } else {
    showPage.detailWidth = 0
  }
}

const showPage = reactive({
  detailWidth: 200
})
onMounted(() => {
  console.log('component is mounted')
})
</script>

<style scoped>
.close-btn {
    margin: 10px 2px;
}
  .common-layout {
    height: 80%;
    display: flex;
    flex-direction: column;
  }
  .el-header {
    background-color: var(--el-color-info-dark-2);
    color: var(--el-color-info-light-9);;
    text-align: left;
    line-height: 30px;
    height: 30px;
  }

  .el-main {
    background-color: #E9EEF3;
    color: var(--el-color-info-light-2);
    text-align: center;
    line-height: 160px;
    display: flex;
    padding: 0;
    overflow: hidden;
  }
  #fileManager {
    background-color: var(--el-color-warning-light-7);
    height: 100%;
    float:left;
    overflow: hidden;
  }
  .el-tree {
    background-color: transparent;
  }
  #codingArea {
    height:100%;
    float:left;
    overflow: hidden;
    background: var(--el-color-danger-light-7);
    flex-grow: 1;
  }
  #codingArea:hover {
    background: var(--el-color-danger-light-5);
  }
  #resize{
    position: relative;
    width:5px;
    height:100%;
    cursor: w-resize;
    float:left;
  }
  body > .el-container {
    margin-bottom: 40px;
  }
</style>

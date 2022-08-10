<template>
  <div class="common-layout">
    <el-container>
      <el-header>
        <el-button type="primary" class="backBtn" :icon="HomeFilled" @click="ProjectBack" text>Menu</el-button>
        <el-button type="primary" class="saveBtn" :icon="Checked" @click="saveProject" text>Save</el-button>
      </el-header>
      <el-container>
        <div class="btnArea">
          <el-button class="closeBtn" :icon="Fold" @click="closeAside" circle />
        </div>
        <el-aside :width="data.width">
          <FileSet :name="name" :projectname="projectname"></FileSet>
        </el-aside>
        <span class="resize_col" @mousedown="handleDragStart"></span>
        <el-container>
          <el-main>Main</el-main>
          <span class="resize_row" @mousedown="handleDragStartrow"></span>
          <el-footer :height="data.height">Footer</el-footer>
        </el-container>
      </el-container>
    </el-container>
  </div>
</template>

<script lang="ts" setup>
import router from '@/router'
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import {
  Fold,
  HomeFilled,
  Checked
} from '@element-plus/icons-vue'

import FileSet from '../components/fileSet.vue'
import { ElNotification } from 'element-plus'
// 获取当前用户名
const name = useRouter().currentRoute.value.params.username

// 获取当前项目名
const projectname = useRouter().currentRoute.value.params.projectname

// 回到当前用户的项目管理区域
const ProjectBack = () => {
  router.replace({ name: 'projectmanage', params: { username: name } })
}

const data = reactive({
  width: '200px',
  old_width: '0px',
  isClose: false,
  originX: 200,
  originY: 20,
  height: '50px',
  old_height: '0px',
  old_height_2: 0,
  height_2: 50
})

// 侧边栏收开
const closeAside = () => {
  if (data.isClose) {
    console.log('isClose')
    data.width = data.old_width
    data.isClose = false
    console.log(data.isClose)
  } else {
    console.log('noClose')
    data.old_width = data.width
    data.width = '0px'
    data.isClose = true
    console.log(data.isClose)
  }
}

// 保存文件
const saveProject = () => {
  console.log('save')
}

// 侧边栏拖拽大小
const handleDragStart = (event: MouseEvent) => {
  data.originX = event.clientX
  console.log(data.originX)
  let isMouseDown = true
  document.onmousemove = (ev:MouseEvent) => {
    if (!isMouseDown) return false
    const moveX = ev.clientX
    console.log(ev.clientX, data.originX, moveX)
    data.old_width = data.width
    data.width = moveX + 'px'
  }
  document.onmouseup = (ev:MouseEvent) => {
    if (!isMouseDown) return false
    isMouseDown = false
  }
}
// debug区域拖拽大小
const handleDragStartrow = (event: MouseEvent) => {
  data.originY = event.clientY
  console.log(data.originY)
  let isMouseDown = true
  data.old_height_2 = data.height_2
  document.onmousemove = (ev:MouseEvent) => {
    if (!isMouseDown) return false
    const moveY = data.originY - ev.clientY
    data.height_2 = data.old_height_2 + moveY
    data.height = data.height_2 + 'px'
    console.log(ev.clientY, data.originY, moveY, data.old_height, data.old_height_2)
  }
  document.onmouseup = (ev:MouseEvent) => {
    if (!isMouseDown) return false
    isMouseDown = false
  }
}
</script>

<style scoped>
div {
  display: flex;
  height: 100%;
}
.el-header {
  background-color: var(--el-color-primary-dark-2);
  height: 30px;
  display: flex;
  flex-direction: row;
  padding: 0 5px;
}
.resize_col {
  cursor: col-resize;
  float: left;
  border-radius: 5px;
  width: 2px;
}
.resize_row {
  cursor:row-resize;
  float: left;
  border-radius: 5px;
  height: 2px;
}
.backBtn, .saveBtn {
  height: 30px;
  background-color: var(--el-color-primary-dark-2);
  color: aliceblue;
  margin: 0;
}
.backBtn:hover, .saveBtn:hover {
  color: black;
}
.backBtn:hover {
  background-color: var(--el-color-primary);
}
.el-footer {
  background-color: var(--el-color-primary-dark-2);
  overflow: auto;
  display: flex;
  flex-direction: column;
}
.el-aside {
  background-color: var(--el-color-primary-light-8);
  overflow: auto;
}
.el-main {
  background-color: var(--el-color-primary-light-7);
  overflow: auto;
}
.btnArea {
  display: flex;
  flex-direction: column;
}
.btnArea .el-button {
  margin: 5px 2px;
}
</style>

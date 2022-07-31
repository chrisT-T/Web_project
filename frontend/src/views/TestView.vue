<template>
  <el-container class="layout-container-demo">
    <el-aside width="200px">
        <el-space direction="vertical">
           <h1>{{ name }}</h1>
           <el-col>
            <el-popconfirm title="Are you sure to logout?" confirmButtonText="logout" @confirm="logoutConfirm">
              <template #reference>
                <el-button size="large">Logout</el-button>
              </template>
            </el-popconfirm>
           </el-col>
        </el-space>
    </el-aside>
    <el-container>
      <el-header style="text-align: right; font-size: 12px">
        <div class="toolbar">
            <el-button type="primary" :icon="Edit" @click="dialogFormVisible = true" circle/>
        </div>
      </el-header>

      <el-main>
        <el-scrollbar max-height="600px">
            <div v-for="( item, index ) in form.taskList" :key="item.id" class="scrollbar-demo-item">
                <div><span>{{item.language}}</span><span>{{item.name}}</span></div>
                <el-button type="danger" :icon="Delete" @click="removeTask(index)" circle />
            </div>
            <span style="color: var(--el-color-info-light-5)">end of list</span>
        </el-scrollbar>
      </el-main>
    </el-container>
  </el-container>

    <el-dialog v-model="dialogFormVisible" title="Create new task" custom-class="createDialog">
      <el-form
        ref="formRef"
        :model="form"
        label-width="60px"
        class="demo-ruleForm"
      >
        <el-form-item
          label="task name"
          :rules="[
            { required: true, message: 'task name is required' }
          ]"
          :label-width="formLabelWidth"
        >
          <el-input v-model="form.name" autocomplete="off"/>
        </el-form-item>
        <el-form-item label="Project language" :label-width="formLabelWidth">
            <el-select v-model="form.language" class="m-2" placeholder="Select">
                <el-option
                v-for="item in options"
                :key="item.value"
                :label="item.label"
                :value="item.value"
                />
            </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm(); dialogFormVisible = false">Submit</el-button>
          <!-- <el-button @click="resetForm(formRef); dialogFormVisible = false">Reset</el-button> -->
        </el-form-item>
      </el-form>
    </el-dialog>
</template>

<script lang="ts" setup>
import { reactive, ref } from 'vue'
import {
  Delete,
  Edit
} from '@element-plus/icons-vue'
import { FormInstance } from 'element-plus'
import router from '@/router'
import { useRouter } from 'vue-router'

const count = ref(0)
const formLabelWidth = '140px'
const formRef = ref<FormInstance>()
// 提交新项目
// TODO：后端确认没有重复项目名
const submitForm = () => {
  if (form.name === '' || form.language === '') {
    console.log('Empty enter form')
  } else {
    form.taskList.unshift({
      name: form.name,
      language: form.language,
      id: count.value++
    })
  }
}
// 登出确认
const logoutConfirm = () => {
  router.replace('/index')
}
// 删除项目
const removeTask = (index: number) => {
  form.taskList.splice(index, 1)
}
// 当前用户名 从rouetr获取
const name = ref(useRouter().currentRoute.value.params.username)

const dialogFormVisible = ref(false)

const form = reactive({
  name: '',
  language: '',
  taskList: [
    { name: 'project 1', language: 'python', id: 0 }
  ]
})

// language options
const options = [
  {
    value: 'python',
    label: 'python'
  }
]
</script>

<style scoped>
.layout-container-demo .el-header {
  position: relative;
  background-color: var(--el-color-primary-light-7);
  color: var(--el-text-color-primary);
}
.layout-container-demo .el-aside {
  color: var(--el-text-color-primary);
  display: flex;
  flex-direction: column;
}
.layout-container-demo .el-menu {
  border-right: none;
}
.layout-container-demo .el-main {
  padding: 0;
}
.layout-container-demo .toolbar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  right: 20px;
}
.scrollbar-demo-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 50px;
  margin: 10px;
  text-align: center;
  border-radius: 4px;
  color: var(--el-color-primary);
  box-shadow: 0px 3px 3px var(--el-color-info-light-7);
}
.scrollbar-demo-item:hover {
    background-color: var(--el-color-info-light-9);
}
.scrollbar-demo-item span, div{
    padding: 0 10px;
}
</style>

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
      <el-header v-if="form.taskList.length > 0">
        <div class="ProjectCnt">
          <span>No. of Project: {{ form.taskList.length }}</span>
        </div>
        <div class="toolbar">
            <el-button type="primary" plain size="default" :icon="Plus" @click="dialogFormVisible = true" circle/>
        </div>
      </el-header>
      <el-main>
        <el-scrollbar max-height="600px" v-if="form.taskList.length > 0">
            <div v-for="( item, index ) in form.taskList" :key="item.id" class="scrollbar-demo-item">
                <div class="detail_info" >
                  <el-link type="info" :underline="false">{{ item.language }}</el-link>
                  <el-link type="primary" :underline="false" :icon="InfoFilled" @click="ProjectDetail(item.name)" v-if="!form.taskList[index].showInp">{{item.name}}</el-link>
                  <el-input class="changeInp" size="large" ref="inputVal" v-if="form.taskList[index].showInp" :value="item.name"
                    v-model="changeInput.inputStr"
                    v-focus="changeInput.isChecked"
                    @blur="editGiveup(index)"
                    @keyup.enter="editFinish(index)"
                    placeholder="file name">
                  </el-input>
                </div>
                <div class="detail_info">
                  <span class="time">{{item.lastupdate}}</span>
                  <el-button type="primary" :icon="Edit" @click="editStart(index)" circle />
                  <el-button type="danger" :icon="Delete" @click="removeTask(index)" circle />
                </div>
            </div>
            <span style="color: var(--el-color-info-light-5)">end of list</span>
        </el-scrollbar>
        <div class="noTask" v-else>
          <span>Welcom to use <span class="codingtitle">CODING-ONLINE</span></span>
          <span>Please start your first Task</span>
          <el-button type="primary" :icon="Plus" plain @click="dialogFormVisible = true">Create new Task</el-button>
        </div>
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
import { onMounted, reactive, ref } from 'vue'
import {
  Delete,
  Edit,
  InfoFilled,
  Plus
} from '@element-plus/icons-vue'
import { ElNotification, FormInstance } from 'element-plus'
import router from '@/router'
import { useRouter } from 'vue-router'
import axios from 'axios'

const count = ref(0)
const formLabelWidth = '140px'
const formRef = ref<FormInstance>()
const changeInput = reactive({
  isChecked: false,
  inputStr: ''
})

// 当前用户名 从rouetr获取
const name = useRouter().currentRoute.value.params.username

const dialogFormVisible = ref(false)
// language options
const options = [
  {
    value: 'python',
    label: 'python'
  }
]

interface Project {
  name: string
  language: string
  id: number
  lastupdate: string
}

const form = reactive({
  name: '',
  language: '',
  flag: false,
  message: '',
  lastupdate: '',
  data: [],
  taskList: [
  //  { name: 'project 1', language: 'python', id: 0, lastupdate: 'time' }
  ],
  isChecked: false
})

// 提交新项目
const submitForm = async () => {
  if (form.name === '' || form.language === '') {
    alert('Empty enter form')
  } else {
    await axios.post('http://127.0.0.1:5000/mkpro/' + name, { src: name + '/' + form.name, type: form.language })
      .then(res => {
        form.flag = res.data.flag
        form.message = res.data.message
        form.lastupdate = res.data.lastupdate
      }).catch(function (error) {
        console.log(error.response)
      })
    if (form.flag === false) {
      alert(form.message)
      return
    }
    form.taskList.unshift({
      name: form.name,
      language: form.language,
      id: count.value++,
      lastupdate: form.lastupdate
    })
  }
}

// 删除项目
const removeTask = async (index: number) => {
  await axios.post('http://127.0.0.1:5000/deletepro/' + name, { src: name + '/' + form.taskList[index].name, type: 'folder' })
    .then(res => {
      form.flag = res.data.flag
      form.message = res.data.message
    }).catch(function (error) {
      console.log(error.response)
    })

  if (form.flag === false) {
    alert(form.message)
    return
  }
  form.taskList.splice(index, 1)
}

const editStart = (index: number) => {
  console.log('editStart' + index)
  if (!changeInput.isChecked) {
    // changeInput.inputStr = item.name
    // changeInput.isChecked = true
    changeInput.inputStr = form.taskList[index].name
    changeInput.isChecked = true
    form.taskList[index].showInp = true
  }
}

const editFinish = async (index: number) => {
  console.log('editFinish' + index)
  await axios.post('http://127.0.0.1:5000/renamepro/' + name, { src: name + '/' + form.taskList[index].name, dst: name + '/' + changeInput.inputStr })
    .then(res => {
      form.flag = res.data.flag
      form.message = res.data.message
    }).catch(function (error) {
      console.log(error.response)
    })
  if (form.flag === false) {
    alert(form.message)
    return
  }
  form.taskList[index].name = changeInput.inputStr
  changeInput.isChecked = false
  form.taskList[index].showInp = false
}
const editGiveup = () => {
  console.log('edirGiveup')
  changeInput.isChecked = false
}

// 跳到项目详情页
const ProjectDetail = (Projectname:string) => {
  console.log(Projectname)
  router.replace({ name: 'coding', params: { username: name, projectname: Projectname } })
}

// 登出确认
const logoutConfirm = async () => {
  await axios.post('http://127.0.0.1:5000/logout/' + name)
    .then(res => {
      form.message = res.data
    }).catch(function (error) {
      console.log(error.response)
    })
  if (form.message !== 'succeed logout') {
    alert('something wrong')
    return
  }
  router.replace('/login')
}

onMounted(async () => {
  // ElNotification({
  //   title: '使用指南 -- Project Management',
  //   message: 'Sidebar for personal information. The information in the main column is: language, project name, last update time, and deleted project',
  //   type: 'info',
  //   duration: 0,
  //   offset: 300
  // })
  await axios.get('http://127.0.0.1:5000/getPro/' + name)
    .then(res => {
      form.data = res.data.data
      form.flag = res.data.flag
    }).catch(function (error) {
      console.log(error.response)
    })
  if (form.flag === false) {
    alert(form.message)
    return
  }
  form.taskList = []
  // let num = form.data.length
  for (var key in form.data) {
    const taskRecord = { name: form.data[key][0], language: form.data[key][1], id: key, lastupdate: form.data[key][2] }
    form.taskList.push(taskRecord)
  }
  form.taskList.sort((a, b) => {
    if (a.lastupdate < b.lastupdate) {
      return 1
    } else {
      return -1
    }
  })
})
</script>

<style scoped>
.layout-container-demo {
  height: 100%;
}
.layout-container-demo .el-header {
  position: relative;
  background-color: var(--el-color-primary-light-7);
  color: var(--el-text-color-primary);
  justify-content: space-between;
  display: flex;
  flex-direction: row;
}
.ProjectCnt {
  margin-top: 6px;
}
.ProjectCnt span {
  font-size: 30px;
  color: var(--el-color-primary-dark-2);
  font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif ;
}
.layout-container-demo .el-aside {
  color: var(--el-text-color-primary);
  display: flex;
  flex-direction: column;
  background-color: var(--el-color-primary-light-9);
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
.scrollbar-demo-item .el-link, div{
  padding: 0 10px;
}
.el-link {
  font-size: 18px;
}
.el-select {
  width: 60%;
}
.el-input {
  width: 90%;
}
.time {
  margin: 40px;
}
.detail_info {
  overflow: hidden;
  white-space: nowrap;
}
.noTask {
  height: 50%;
  width: 70%;
  max-width: 500px;
  max-height: 200px;
  min-width: 300px;
  min-height: 150px;
  box-shadow: rgb(0 0 0 / 27%) 1px 6px 20px;
  border-radius: 20px;
  margin: 25% auto;
  display: flex;
  flex-direction: column;
  Vertical-align:middle;
  align-items: center;
  justify-content: center;
  flex-wrap: nowrap
}
.codingtitle {
  color: var(--el-color-primary);
  font-family: 'Courier New', Courier, monospace;
  font-weight: bolder;
}
.noTask span {
  margin-bottom: 25px;
}
.noTask .el-button {
  width: 200px;
  height: 40px;
}
</style>

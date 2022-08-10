<template>
  <div class="custom-tree-container">
    <el-tree
      :data="dataSource"
      node-key="id"
      default-expand-all
    >
      <template #default="{ node, data }">
        <span class="custom-tree-node">
          <el-dropdown v-if="!data.showInput" trigger="contextmenu">
            <span class="el-dropdown-link" @dblclick="editStart(data)">
              {{ node.label }}
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item :icon="Plus" @click="currentTree(data)" :disabled="data.type === 'file'">Append</el-dropdown-item>
                <el-dropdown-item :icon="DeleteFilled" @click="remove(node, data)">Delete</el-dropdown-item>
                <el-dropdown-item :icon="EditPen" @click="editStart(data)">Change name</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-input size="small" ref="inputVal" v-if="data.showInput" :value="data.label"
            v-model="changeInput.inputStr"
            v-focus="data.showInput"
            @blur="editGiveup(data)"
            @keyup.enter="editFinish(data)"
            placeholder="file name">
          </el-input>
        </span>
      </template>
    </el-tree>
    <el-dialog v-model="form.dialogFormVisible" title="Create new file/folder">
      <el-form :model="form">
        <el-form-item label="Name" :label-width="formLabelWidth">
          <el-input v-model="form.label" autocomplete="off" />
        </el-form-item>
        <el-form-item label="Type" :label-width="formLabelWidth">
          <el-select v-model="form.type" placeholder="Please select type">
            <el-option :icon="DocumentAdd" label="Folder" value="folder" />
            <el-option :icon="FolderAdd" label="File" value="file" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="form.dialogFormVisible = false">Cancel</el-button>
          <el-button type="primary" @click="form.dialogFormVisible = false; submitCheck(form.currennode, form.label, form.type)"
            >Confirm</el-button
          >
        </span>
      </template>
    </el-dialog>
</div>
</template>

<script lang="ts" setup>
import { ref, reactive } from 'vue'
import Node from 'element-plus/es/components/tree/src/model/node'
import {
  Plus,
  DeleteFilled,
  DocumentAdd,
  FolderAdd,
  EditPen
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const formLabelWidth = '140px'
const props = defineProps({
  name: String
})

interface Tree {
  id: number
  label: string
  type: string
  route: string
  showInput: boolean
  children?: Tree[]
}
let id = 10000

const form = reactive({
  dialogFormVisible: false,
  label: '',
  type: '',
  currennode: {
    id: 0,
    label: '',
    type: '',
    route: '',
    showInput: false
  },
  flag: false,
  message: ''
})

const changeInput = reactive({
  isChecked: false,
  inputStr: ''
})
// 成功编辑并连接后端
const editFinish = async (data:Tree) => {
  let editCheck = true
  const reg = /.py$/
  if (!reg.test(changeInput.inputStr) && data.type === 'file') {
    editCheck = false
  }
  if (editCheck) {
    await axios.post('http://127.0.0.1:5000/rename/' + props.name, { src: props.name + '/' + data.label, dst: props.name + '/' + changeInput.inputStr })
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
    data.label = changeInput.inputStr
    data.showInput = false
    changeInput.isChecked = false
  } else {
    ElMessage({
      message: 'Warning, ,py is missing',
      type: 'warning'
    })
  }
  console.log(data.label, changeInput.inputStr)
}
// 开始编辑
const editStart = (data:Tree) => {
  console.log('alters')
  if (!changeInput.isChecked) {
    changeInput.inputStr = data.label
    data.showInput = !data.showInput
    changeInput.isChecked = true
  }
}
// 放弃编辑
const editGiveup = (data:Tree) => {
  console.log('alter')
  changeInput.isChecked = false
  data.showInput = false
}

const currentTree = (data: Tree) => {
  form.currennode = data
  console.log(form.currennode)
  // 文件不能继续新增加
  if (data.type !== 'file') {
    form.dialogFormVisible = true
  }
}

// 创建新文件/文件夹
const submitCheck = async (data: Tree, labelNew: string, typeNew: string) => {
  if (labelNew === '' || typeNew === '') {
    alert('Name or type is missing')
  } else {
    if (typeNew === 'file') {
      labelNew = labelNew + '.py'
      console.log(labelNew)
      console.log(data.route)
      await axios.post('http://127.0.0.1:5000/touch/' + props.name, { src: props.name + '/' + data.route + '/' + labelNew})
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
    }
    else {
      await axios.post('http://127.0.0.1:5000/mkdir/' + props.name, { src: props.name + '/' + data.route + '/' + labelNew})
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
    }
    const newChild = { id: id++, label: labelNew, type: typeNew, route: data.route + '/' + data.label, showInput: false, children: [] }
    console.log(newChild)
    if (!data.children) {
      data.children = []
    }
    data.children.push(newChild)
    dataSource.value = [...dataSource.value]
  }
}

// 删除文件/文件夹
const remove = async (node: Node, data: Tree) => {
  await axios.post('http://127.0.0.1:5000/delete/' + props.name, { src: props.name + '/' + data.route + '/' + data.label, type: data.type})
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
  const parent = node.parent
  const children: Tree[] = parent.data.children || parent.data
  const index = children.findIndex((d) => d.id === data.id)
  children.splice(index, 1)
  dataSource.value = [...dataSource.value]
}

// TODO: 从后端获取这个项目的文件信息：需要增加id

const dataSource = ref<Tree[]>([
  {
    id: 1,
    label: 'Level one 1',
    type: 'folder',
    route: '',
    showInput: false,
    children: [
      {
        id: 4,
        label: 'Level two 1-1',
        type: 'folder',
        route: 'Level one 1',
        showInput: false,
        children: [
          {
            id: 9,
            label: 'Level three 1-1-1',
            type: 'folder',
            route: 'Level one 1\\Level two 1-1',
            showInput: false
          },
          {
            id: 10,
            label: 'Level_three_1-1-2.py',
            type: 'file',
            route: 'Level one 1\\Level two 1-1',
            showInput: false
          }
        ]
      }
    ]
  },
  {
    id: 2,
    label: 'Level one 2',
    type: 'folder',
    route: '',
    showInput: false,
    children: [
      {
        id: 5,
        label: 'Level two 2-1',
        type: 'folder',
        route: 'Level one 2',
        showInput: false
      },
      {
        id: 6,
        label: 'Level_two_2-2.py',
        type: 'file',
        route: 'Level one 2',
        showInput: false
      }
    ]
  },
  {
    id: 3,
    label: 'Level one 3',
    type: 'folder',
    route: '',
    showInput: false,
    children: [
      {
        id: 7,
        label: 'Level two 3-1',
        type: 'folder',
        route: 'Level one 3',
        showInput: false
      },
      {
        id: 8,
        label: 'Level_two_3-2.py',
        type: 'file',
        route: 'Level one 3',
        showInput: false
      }
    ]
  }
])
</script>

<style>
.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}
.el-select {
  width: 70%;
}
.el-input {
  width: 70%;
}
.dialog-footer button:first-child {
  margin-right: 10px;
}
.el-dialog {
  overflow: auto;
}
.el-tree {
  width: 100%;
  background-color: transparent;
}
</style>

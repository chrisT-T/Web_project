<template>
  <div class="custom-tree-container">
    <el-tree
      :data="dataSource"
      node-key="id"
      default-expand-all
      :indent="5"
      @node-click="handleNodeClick"
    >
      <template #default="{ node, data }">
        <span v-if="!data.isRoot" class="custom-tree-node">
          <el-dropdown v-if="!data.showInput" trigger="contextmenu">
            <span class="el-dropdown-link" @dblclick="editStart(data)">
              {{ node.label }}
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item :icon="Plus" @click="currentTree(data)" :disabled="data.type === 'file'">Append</el-dropdown-item>
                <el-dropdown-item :icon="DeleteFilled" @click="remove(node, data)">Delete</el-dropdown-item>
                <el-dropdown-item :icon="EditPen" @click="editStart(data)">Change name</el-dropdown-item>
                <el-dropdown-item :icon="EditPen" @click="debugStart(data)">Run in Debug mode</el-dropdown-item>
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
        <span v-else class="tree-root">
          <span class="el-dropdown-link" v-if="!data.showInput" @dblclick="editStart(data)">
            {{ node.label }}
          </span>
          <span class="tree-root-btn-gp" v-if="!data.showInput">
            <el-button class="tree-btn" :icon="Plus" @click="currentTree(data)" text />
            <el-button class="tree-btn" :icon="EditPen" style="margin: 0px; padding: 0px" @click="editStart(data)" text />
          </span>
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
import { onMounted, ref, reactive } from 'vue'
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
  name: String,
  projectname: String
})

// eslint-disable-next-line func-call-spacing
const emit = defineEmits<{
  (e : 'debugStart', path :string) : void,
  (e : 'openFile', path: string) : void,
}>()
// Tree接口
interface Tree {
  // id: number
  label: string
  type: string
  route: string
  showInput: boolean
  isRoot?: boolean
  children?: Tree[]
}
let id = 10000

// 创建新文件/文件夹表单信息
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
  message: '',
  data: []
})

// 更改文件名
const changeInput = reactive({
  isChecked: false,
  inputStr: ''
})

// 点击某个节点触发
const handleNodeClick = (data: Tree, node: Node) => {
  if (data.type === 'file') {
    console.log('是可打开文件')
    emit('openFile', data.route + '/' + data.label)
  }
  console.log('node click')
  console.log(data)
  console.log(node)
}

// 在某个文件夹被重命名后，将该文件夹中的文件及文件夹的 route 更新
function changeRoute (children: Tree[], pre: string, origin: string, newLabel: string) {
  for (var key in children) {
    children[key].route = pre + '/' + newLabel + children[key].route.slice(pre.length + 1 + origin.length)
    if (children[key].type === 'folder') {
      changeRoute(children[key].children, pre, origin, newLabel)
    }
  }
}
// 成功编辑并连接后端
const editFinish = async (data:Tree) => {
  let editCheck = true
  const reg = /.py$/
  if (!reg.test(changeInput.inputStr) && data.type === 'file') {
    editCheck = false
  }
  if (editCheck) {
    await axios.post('/api/rename/' + props.name, { src: props.name + '/' + data.route + '/' + data.label, dst: props.name + '/' + data.route + '/' + changeInput.inputStr })
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
    const pre = data.route
    const origin = data.label
    const newLabel = changeInput.inputStr
    changeRoute(data.children, pre, origin, newLabel)
    data.label = newLabel
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
// 获得当前节点
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
      await axios.post('/api/touch/' + props.name, { src: props.name + '/' + data.route + '/' + data.label + '/' + labelNew })
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
    } else {
      await axios.post('/api/mkdir/' + props.name, { src: props.name + '/' + data.route + '/' + data.label + '/' + labelNew })
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
  await axios.post('/api/delete/' + props.name, { src: props.name + '/' + data.route + '/' + data.label, type: data.type })
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

// 文件树的数据结构
const dataSource = ref<Tree[]>([
  {
    // id: 1,
    label: props.projectname,
    type: 'folder',
    route: '',
    isRoot: true,
    showInput: false,
    children: []
  }
])

// 将从后端拿到的文件树的数据填充到前端的 dataSource 中去
function fillData (children: Tree[], data: object) {
  for (var key in data) {
    const tree = { label: data[key].label, type: data[key].type, route: data[key].route, showInput: data[key].showInput, isRoot: data[key].isRoot, children: [] }
    children.push(tree)
    if (data[key].type === 'folder') {
      fillData(tree.children, data[key].children)
    }
  }
}

// code for debugger

const debugStart = (data:Tree) => {
  const filepath = props.name + '/' + data.route + '/' + data.label as string
  console.log(filepath)
  emit('debugStart', filepath)
}

// 每次加载页面时从后端拿文件树
onMounted(async () => {
  await axios.get('/api/getFileTree/' + props.name + '/' + props.projectname)
    .then(res => {
      form.flag = res.data.flag
      form.message = res.data.message
      form.data = res.data.fileTree
    }).catch(function (error) {
      console.log(error.response)
    })
  if (form.flag === false) {
    alert(form.message)
    return
  }
  fillData(dataSource.value[0].children, form.data)
})

</script>

<style scoped>
.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
  width: 100%;
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
.tree-btn {
  margin: 0;
}
.tree-root {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.tree-root-btn-gp {
  margin-right: 15px;
}
</style>

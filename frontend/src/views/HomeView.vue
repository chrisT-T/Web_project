<template>
  <div class="home">
    <img alt="Vue logo" src="../assets/logo.png">
    <HelloWorld msg="Welcome to Your Vue.js + TypeScript App"/>
    <MonacoEditor :editor-option="option" ref="myeditor"> </MonacoEditor>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component'
import HelloWorld from '@/components/HelloWorld.vue' // @ is an alias to /src
import MonacoEditor from '@/components/MonacoEditor/MonacoEditor.vue'

@Options({
  components: {
    HelloWorld,
    MonacoEditor
  }
})
export default class HomeView extends Vue {
  option = {
    theme: 'vs'
  }

  mounted () {
    console.log('mounted')
    console.log(this.option)
    setTimeout(() => {
      this.option.theme = 'vs-dark'
    }, 5000)
  }
}
</script>

<template>
  <div class="home">
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
    theme: 'vs-dark',
    glyphMargin: true,
    language: 'python'
  }

  mounted () {
    console.log('HomeView mounted')
  }
}
</script>

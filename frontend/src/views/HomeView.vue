<template>
  <div class="home">
    <!-- <MonacoEditor :editor-option="option" ref="myeditor"> </MonacoEditor> -->
    <EditorSelf></EditorSelf>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component'
import HelloWorld from '@/components/HelloWorld.vue' // @ is an alias to /src
import MonacoEditor from '@/components/EditorPanel/MonacoEditor/MonacoEditor.vue'
import EditorSelf from '@/components/EditorPanel/EditorSelf.vue'

@Options({
  components: {
    HelloWorld,
    MonacoEditor,
    EditorSelf
  }
})
export default class HomeView extends Vue {
  option = {
    theme: 'vs-dark',
    glyphMargin: true,
    language: 'python'
  }

  mounted () {
    console.log('mounted')
  }
}
</script>

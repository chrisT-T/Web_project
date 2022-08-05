<template>
  <div class="home">
    <!-- <MonacoEditor :editor-option="option" ref="myeditor"> </MonacoEditor> -->
    <EditorPanel></EditorPanel>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component'
import HelloWorld from '@/components/HelloWorld.vue' // @ is an alias to /src
import EditorPanel from '@/components/EditorPanel/EditorPanel.vue'

@Options({
  components: {
    HelloWorld,
    EditorPanel
  }
})
export default class HomeView extends Vue {
  mounted () {
    console.log('mounted')
  }
}
</script>

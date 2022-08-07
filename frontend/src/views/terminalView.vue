<template>
  <div>
    <h1>Web terminal</h1>
    <!-- <web-terminal termName='webterm'/> -->
    <web-debugger debuggerName='debugterm'/>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component'
// import webTerminal from '@/components/webTerminal.vue'
import webDebugger from '@/components/webDebugger.vue'
@Options({
  components: {
    // webTerminal
    webDebugger

  }
})
export default class terminalView extends Vue {}
</script>

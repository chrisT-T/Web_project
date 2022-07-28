<template>
  <div>
    <h1>Web terminal</h1>
    <web-debugger debuggerName='debugterm'/>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component'
// import webTerminal from '@/components/webTerminal.vue'
import webDebugger from '@/components/webDebugger.vue'
@Options({
  components: {
    webDebugger
  }
})
export default class terminalView extends Vue {}
</script>

<template>
  <div>
    <h1>Web terminal</h1>
    <web-terminal termName='term'/>
    <web-terminal termName='newTerm'/>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component'
import webTerminal from '@/components/webTerminal.vue'

@Options({
  components: {
    webTerminal
  }
})
export default class terminalView extends Vue {}
</script>

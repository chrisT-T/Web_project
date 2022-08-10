<template>
  <div>
    <h1>Web terminal</h1>
    <!-- <web-terminal termName='webterm'/> -->
    <web-debugger filePath='./test_script/test.py'/>
  </div>
</template>

<script lang="ts" setup>
// import webTerminal from '@/components/webTerminal.vue'
import webDebugger from '@/components/webDebugger.vue'
</script>

<template>
  <div id="editor" ref="editor"></div>
</template>

<script lang="ts">
import * as monaco from 'monaco-editor'
import { Options, Vue } from 'vue-class-component'
import { toRaw } from 'vue'

@Options({
  props: {
    editorOption: {
      type: Object,
      default: () => ({
        theme: 'vs'
      })
    }
  },
  watch: {
    editorOption: {
      handler (val) {
        console.log(val)
        this.getEditor().updateOptions(val)
      },
      deep: true
    }
  }
})
export default class MonacoEditor extends Vue {
  editor!: monaco.editor.IStandaloneCodeEditor
  mounted () {
    console.log('mounted')
    // console.log(this.option)
    this.editor = monaco.editor.create(this.$refs.editor as HTMLElement, {})
  }

  destroyed () {
    console.log('destroyed')
    this.editor.dispose()
  }

  getEditor () {
    return this.editor
  }
}
</script>

<style src="./main.css"/>

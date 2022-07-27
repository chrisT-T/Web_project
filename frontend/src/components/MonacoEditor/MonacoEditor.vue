<template>
  <div id="editor" ref="editor"></div>
</template>

<script lang="ts">
import * as monaco from 'monaco-editor'
import { Options, Vue } from 'vue-class-component'

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
        console.log('editor options:')
        console.log(val)
        this.getEditor().updateOptions(val)
      },
      deep: true
    }
  }
})
export default class MonacoEditor extends Vue {
  editor!: monaco.editor.IStandaloneCodeEditor
  editorOption!: monaco.editor.IStandaloneEditorConstructionOptions

  getAllDecorationbyClass (className : string) {
    return this.editor.getModel()?.getAllDecorations()
      .filter(decoration => decoration.options.glyphMarginClassName === className)
  }

  clearAllDecorationbyClass (className : string) {
    const decorations = this.getAllDecorationbyClass(className)?.map(decoration => decoration.id)
    if (decorations) {
      this.editor.deltaDecorations(decorations, [])
    }
  }

  existDecoration (className: string, lineNumber: number) {
    return this.getAllDecorationbyClass(className)?.some(decoration => decoration.range.startLineNumber === lineNumber)
  }

  addDecoration (className: string, lineNumber: number, hoverMessage : string) {
    const old = this.getAllDecorationbyClass(className) as monaco.editor.IModelDecoration[]
    const oldId = old.map(decoration => decoration.id)
    const existIndex = old.findIndex(decoration => decoration.range.startLineNumber === lineNumber)
    // doesn't exist a decoration on the line
    if (existIndex === -1) {
      old.push({
        id: '',
        ownerId: 0,
        range: new monaco.Range(lineNumber, 1, lineNumber, 1),
        options: {
          isWholeLine: true,
          glyphMarginClassName: className,
          stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
          glyphMarginHoverMessage: {
            value: hoverMessage
          }
        }
      })
      this.editor.deltaDecorations(oldId, old)
    }
  }

  removeDecoration (className: string, lineNumber: number) {
    const old = this.getAllDecorationbyClass(className) as monaco.editor.IModelDecoration[]
    const oldId = old.map(decoration => decoration.id)
    const existIndex = old.findIndex(decoration => decoration.range.startLineNumber === lineNumber)
    // exist a decoration on the line
    if (existIndex !== -1) {
      old.splice(existIndex, 1)
      this.editor.deltaDecorations(oldId, old)
    }
  }

  mounted () {
    const breakpointClassName = 'monaco-editor-breakpoint'
    const shadowBreakpointClassName = 'monaco-editor-breakpoint-shadow'
    console.log('mounted')
    this.editor = monaco.editor.create(this.$refs.editor as HTMLElement, this.editorOption)
    // set shadow on move
    this.editor.onMouseMove(e => {
      const { target } = e
      if (target.type === monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN ||
          target.type === monaco.editor.MouseTargetType.GUTTER_LINE_DECORATIONS) {
        if (!this.existDecoration(breakpointClassName, target.position.lineNumber)) {
          this.clearAllDecorationbyClass(shadowBreakpointClassName)
          this.addDecoration(shadowBreakpointClassName, target.position.lineNumber, '')
        }
      } else {
        this.clearAllDecorationbyClass(shadowBreakpointClassName)
      }
    })
    // clear shadow on leave
    this.editor.onMouseLeave(e => {
      this.clearAllDecorationbyClass(shadowBreakpointClassName)
    })
    // set breakpoint property to the editor
    this.editor.onMouseDown(e => {
      const { target } = e
      if (target.type === monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN || target.type === monaco.editor.MouseTargetType.GUTTER_LINE_DECORATIONS) {
        this.clearAllDecorationbyClass(shadowBreakpointClassName)
        if (!this.existDecoration(breakpointClassName, target.position.lineNumber)) {
          this.addDecoration(breakpointClassName, target.position.lineNumber, '')
        } else {
          this.removeDecoration(shadowBreakpointClassName, target.range.startLineNumber)
          this.removeDecoration(breakpointClassName, target.position.lineNumber)
        }
      }
    })
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

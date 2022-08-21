<template>
  <div class="monaco-editor-container" ref="editorContainer"></div>
</template>

<script lang="ts" setup>
import { ref, onMounted, shallowRef, onUnmounted, watch, defineProps, defineExpose, defineEmits } from 'vue'

import * as monaco from 'monaco-editor'
import * as common from '../common'
// import { buildWorkerDefinition } from 'monaco-editor-workers'

import { MonacoLanguageClient, CloseAction, ErrorAction, MonacoServices, MessageTransports } from 'monaco-languageclient'
import { toSocket, WebSocketMessageReader, WebSocketMessageWriter } from 'vscode-ws-jsonrpc'
import normalizeUrl from 'normalize-url'
// import { StandaloneServices } from 'vscode/services'
// import getMessageServiceOverride from 'vscode/service-override/messages'

const props = defineProps<{
    editorOption: monaco.editor.IStandaloneEditorConstructionOptions,
}>()

const editor = shallowRef<monaco.editor.IStandaloneCodeEditor | null>(null)

const editorContainer = ref<HTMLElement | null>(null)

watch(() => props.editorOption, (val : monaco.editor.IStandaloneEditorConstructionOptions) => {
  console.log(val)
  editor.value?.updateOptions(val)
}, { deep: true })

function setModel (model : monaco.editor.ITextModel) {
  editor.value?.setModel(model)
}
function getAllDecorationbyClass (className : string) {
  return editor.value?.getModel()?.getAllDecorations()
    .filter(decoration => decoration.options.glyphMarginClassName === className)
}

function clearAllDecorationbyClass (className: string) {
  const decorations = getAllDecorationbyClass(className)?.map(decoration => decoration.id)
  if (decorations) {
    editor.value?.getModel()?.deltaDecorations(decorations, [])
  }
}

function existDecoration (className: string, lineNumber: number) {
  return getAllDecorationbyClass(className)?.some(decoration => decoration.range.startLineNumber === lineNumber)
}

function addDecoration (className: string, lineNumber: number, hoverMessage: string) {
  const old = getAllDecorationbyClass(className) as monaco.editor.IModelDecoration[]
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
    editor.value?.getModel()?.deltaDecorations(oldId, old)
  }
}

function removeDecoration (className: string, lineNumber: number) {
  const old = getAllDecorationbyClass(className) as monaco.editor.IModelDecoration[]
  const oldId = old.map(decoration => decoration.id)
  const existIndex = old.findIndex(decoration => decoration.range.startLineNumber === lineNumber)
  // exist a decoration on the line
  if (existIndex !== -1) {
    old.splice(existIndex, 1)
    editor.value?.getModel()?.deltaDecorations(oldId, old)
  }
}

function createLanguageClient (transports: MessageTransports): MonacoLanguageClient {
  return new MonacoLanguageClient({
    name: 'Sample Language Client',
    clientOptions: {
      // use a language id as a document selector
      documentSelector: ['python'],
      // disable the default error handler
      errorHandler: {
        error: () => ({ action: ErrorAction.Continue }),
        closed: () => ({ action: CloseAction.DoNotRestart })
      }
    },
    // create a language client connection from the JSON RPC connection on demand
    connectionProvider: {
      get: () => {
        return Promise.resolve(transports)
      }
    }
  })
}

function createUrl (hostname: string, path: string, port?: number): string {
  const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
  if (port !== undefined) {
    return normalizeUrl(`${protocol}://${hostname}:${port}${path}`)
  } else {
    return normalizeUrl(`${protocol}://${hostname}${path}`)
  }
}

onMounted(() => {
  // StandaloneServices.initialize({
  //   ...getMessageServiceOverride(document.body)
  // })
  // buildWorkerDefinition('dist', new URL('', window.location.href).href, false)

  console.log('Monaco Editor mounted')
  if (editorContainer.value !== null && props.editorOption !== null) {
    editor.value = monaco.editor.create(editorContainer.value, props.editorOption)
  } else {
    console.error('editor container is null')
  }

  // create save and modify emitter
  editor.value?.onDidChangeModelContent(() => {
    emit('modified')
  })

  editor.value?.addAction({
    // An unique identifier of the contributed action.
    id: 'save-current-file',

    // A label of the action that will be presented to the user.
    label: 'Save',

    // An optional array of keybindings for the action.
    keybindings: [
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS
    ],

    // A precondition for this action.
    precondition: undefined,

    // A rule to evaluate on top of the precondition in order to dispatch the keybindings.
    keybindingContext: undefined,

    contextMenuGroupId: 'navigation',

    contextMenuOrder: 1.5,

    // Method that will be executed when the action is triggered.
    // @param editor The editor instance is passed in as a convenience
    run: function () {
      emit('saved')
    }
  })

  // editor.value?.addAction({
  //   // An unique identifier of the contributed action.
  //   id: 'split-current-view-horizontal',

  //   // A label of the action that will be presented to the user.
  //   label: 'Split Current View(Horizontal)',

  //   // An optional array of keybindings for the action.
  //   keybindings: [
  //     monaco.KeyMod.CtrlCmd | monaco.KeyCode.Backslash
  //   ],

  //   // A precondition for this action.
  //   precondition: undefined,

  //   // A rule to evaluate on top of the precondition in order to dispatch the keybindings.
  //   keybindingContext: undefined,

  //   contextMenuGroupId: 'modification',

  //   contextMenuOrder: 1.5,

  //   // Method that will be executed when the action is triggered.
  //   // @param editor The editor instance is passed in as a convenience
  //   run: function () {
  //     emit('splitCurrentView', 'horizontal')
  //   }
  // })

  // editor.value?.addAction({
  //   // An unique identifier of the contributed action.
  //   id: 'split-current-view-vertical',

  //   // A label of the action that will be presented to the user.
  //   label: 'Split Current View(Vertical)',

  //   // An optional array of keybindings for the action.
  //   keybindings: [
  //     monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.Backslash
  //   ],

  //   // A precondition for this action.
  //   precondition: undefined,

  //   // A rule to evaluate on top of the precondition in order to dispatch the keybindings.
  //   keybindingContext: undefined,

  //   contextMenuGroupId: 'modification',

  //   contextMenuOrder: 1.5,

  //   // Method that will be executed when the action is triggered.
  //   // @param editor The editor instance is passed in as a convenience
  //   run: function () {
  //     emit('splitCurrentView', 'vertical')
  //   }
  // })

  editor.value?.onDidFocusEditorText(() => {
    emit('changeCursorFocus')
  })

  // for lint service
  // install the service
  MonacoServices.install()

  // create websocket
  const url = createUrl(location.host, '/lsp')
  const webSocket = new WebSocket(url)

  // define the connection(websocket) to the language server
  webSocket.onopen = () => {
    const socket = toSocket(webSocket)
    const reader = new WebSocketMessageReader(socket)
    const writer = new WebSocketMessageWriter(socket)
    const languageClient = createLanguageClient({ reader, writer })
    languageClient.start()
    reader.onClose(() => languageClient.stop())
  }

  // set shadow on move
  editor.value?.onMouseMove(e => {
    const { target } = e
    if (target.type === monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN ||
      target.type === monaco.editor.MouseTargetType.GUTTER_LINE_DECORATIONS) {
      if (!existDecoration(common.breakPointClassName, target.position.lineNumber)) {
        clearAllDecorationbyClass(common.shadowBreakpointClassName)
        addDecoration(common.shadowBreakpointClassName, target.position.lineNumber, '')
      }
    } else {
      clearAllDecorationbyClass(common.shadowBreakpointClassName)
    }
  })
  // clear shadow on leave
  editor.value?.onMouseLeave(() => {
    clearAllDecorationbyClass(common.shadowBreakpointClassName)
  })
  // set breakpoint property to the editor
  editor.value?.onMouseDown(e => {
    const { target } = e
    if (target.type === monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN || target.type === monaco.editor.MouseTargetType.GUTTER_LINE_DECORATIONS) {
      clearAllDecorationbyClass(common.shadowBreakpointClassName)
      if (!existDecoration(common.breakPointClassName, target.position.lineNumber)) {
        addDecoration(common.breakPointClassName, target.position.lineNumber, '')
      } else {
        removeDecoration(common.shadowBreakpointClassName, target.range.startLineNumber)
        removeDecoration(common.breakPointClassName, target.position.lineNumber)
      }
    }
  })
})

function locateToLine (lineNumber: number) {
  // console error when lineNumber is not valid
  const lineCount = editor.value?.getModel()?.getLineCount() as number
  if (lineNumber < 1 || lineNumber > lineCount) {
    console.error('line number is not valid')
  }
  editor.value?.revealLineInCenter(lineNumber)
  editor.value?.setPosition({ lineNumber, column: 1 })
}

onUnmounted(() => {
  console.log('Monaco Editor Destroyed')
  editor.value?.dispose()
})

defineExpose({
  setModel,
  locateToLine
})

// eslint-disable-next-line func-call-spacing
const emit = defineEmits<{
  (e: 'modified'): void
  (e: 'saved'): void
  (e: 'splitCurrentView', direction: 'horizontal' | 'vertical'): void
  (e: 'changeCursorFocus'): void
}> ()
</script>

<style src="./main.css"/>

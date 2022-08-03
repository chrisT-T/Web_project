<template>
  <div id="editor" ref="editorContainer"></div>
</template>

<script lang="ts" setup>
import { ref, onMounted, shallowRef, onUnmounted, watch, defineProps, defineExpose, defineEmits } from 'vue'

import * as monaco from 'monaco-editor'
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

const models = shallowRef<Array<monaco.editor.ITextModel>>([])

watch(() => props.editorOption, (val : monaco.editor.IStandaloneEditorConstructionOptions) => {
  console.log('editor options:')
  console.log(val)
  editor.value?.updateOptions(val)
}, { deep: true })

function createModel (value: string, language: string) {
  console.log('create model')
  const model = monaco.editor.createModel(value, language)
  models.value.push(model)
  return model
}

function setModel (index : number) {
  console.log('set model')
  editor.value?.setModel(models.value[index])
}

function deleteModel (index : number) {
  models.value[index].dispose()
  models.value.splice(index, 1)
}

function getAllDecorationbyClass (className : string) {
  return editor.value?.getModel()?.getAllDecorations()
    .filter(decoration => decoration.options.glyphMarginClassName === className)
}

function clearAllDecorationbyClass (className: string) {
  const decorations = getAllDecorationbyClass(className)?.map(decoration => decoration.id)
  if (decorations) {
    editor.value?.deltaDecorations(decorations, [])
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
    editor.value?.deltaDecorations(oldId, old)
  }
}

function removeDecoration (className: string, lineNumber: number) {
  const old = getAllDecorationbyClass(className) as monaco.editor.IModelDecoration[]
  const oldId = old.map(decoration => decoration.id)
  const existIndex = old.findIndex(decoration => decoration.range.startLineNumber === lineNumber)
  // exist a decoration on the line
  if (existIndex !== -1) {
    old.splice(existIndex, 1)
    editor.value?.deltaDecorations(oldId, old)
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

function createUrl (hostname: string, port: number, path: string): string {
  const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
  return normalizeUrl(`${protocol}://${hostname}:${port}${path}`)
}

onMounted(() => {
  // StandaloneServices.initialize({
  //   ...getMessageServiceOverride(document.body)
  // })
  // buildWorkerDefinition('dist', new URL('', window.location.href).href, false)

  const breakpointClassName = 'monaco-editor-breakpoint'
  const shadowBreakpointClassName = 'monaco-editor-breakpoint-shadow'
  console.log('mounted')
  if (editorContainer.value !== null && props.editorOption !== null) {
    editor.value = monaco.editor.create(editorContainer.value, props.editorOption)
  } else {
    console.error('editor container is null')
  }

  // create save and modify emitter
  editor.value?.onDidChangeModelContent((e) => {
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
    run: function (ed) {
      emit('saved')
    }
  })

  // for lint service
  // install the service
  MonacoServices.install()

  // create websocket
  const url = createUrl('localhost', 3000, '/')
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
      if (!existDecoration(breakpointClassName, target.position.lineNumber)) {
        clearAllDecorationbyClass(shadowBreakpointClassName)
        addDecoration(shadowBreakpointClassName, target.position.lineNumber, '')
      }
    } else {
      clearAllDecorationbyClass(shadowBreakpointClassName)
    }
  })
  // clear shadow on leave
  editor.value?.onMouseLeave(() => {
    clearAllDecorationbyClass(shadowBreakpointClassName)
  })
  // set breakpoint property to the editor
  editor.value?.onMouseDown(e => {
    const { target } = e
    if (target.type === monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN || target.type === monaco.editor.MouseTargetType.GUTTER_LINE_DECORATIONS) {
      clearAllDecorationbyClass(shadowBreakpointClassName)
      if (!existDecoration(breakpointClassName, target.position.lineNumber)) {
        addDecoration(breakpointClassName, target.position.lineNumber, '')
      } else {
        removeDecoration(shadowBreakpointClassName, target.range.startLineNumber)
        removeDecoration(breakpointClassName, target.position.lineNumber)
      }
    }
  })
})

onUnmounted(() => {
  console.log('destroyed')
  editor.value?.dispose()
})

defineExpose({
  createModel,
  setModel,
  deleteModel
})

// eslint-disable-next-line func-call-spacing
const emit = defineEmits<{
  (e: 'modified'): void
  (e: 'saved'): void
}> ()
</script>

<style src="./main.css"/>

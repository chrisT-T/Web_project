<template>
  <div id="editor" ref="editor"></div>
</template>

<script lang="ts">
import vsDark from './themes/vs-dark-converted.json'
import * as monaco from 'monaco-editor/esm/vs/editor/editor.api'
import { Options, Vue } from 'vue-class-component'

import { buildWorkerDefinition } from 'monaco-editor-workers'
import { StandaloneServices } from 'vscode/services'
import getMessageServiceOverride from 'vscode/service-override/messages'

import { MonacoLanguageClient, CloseAction, ErrorAction, MonacoServices, MessageTransports } from 'monaco-languageclient'
import { toSocket, WebSocketMessageReader, WebSocketMessageWriter } from 'vscode-ws-jsonrpc'
import normalizeUrl from 'normalize-url'

import { loadWASM, createOnigString, createOnigScanner } from 'vscode-oniguruma'
import { Registry, IRawGrammar, parseRawGrammar, INITIAL } from 'vscode-textmate'
import { createTextmateTokenizer, TextmateRegistry, TokenizerState } from './textmate'
import { languageContributions } from './lanuages/language'

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

  createLanguageClient (transports: MessageTransports): MonacoLanguageClient {
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

  createUrl (hostname: string, port: number, path: string): string {
    const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
    return normalizeUrl(`${protocol}://${hostname}:${port}${path}`)
  }

  async fetchOnigasm (): Promise<ArrayBuffer | Response> {
    const response = await fetch('onig.wasm')
    const contentType = response.headers.get('content-type')
    if (contentType === 'application/wasm') {
      return response
    }
    return await response.arrayBuffer()
  }

  async mounted () {
    // StandaloneServices.initialize({
    //   ...getMessageServiceOverride(document.body)
    // })
    // buildWorkerDefinition('dist', new URL('', window.location.href).href, false)

    // 注册我们需要的语言
    monaco.languages.register({ id: 'python' })

    // load wasm
    await this.fetchOnigasm().then(async (res) => {
      await loadWASM(res)
    })

    const textmateRegistry = new TextmateRegistry()

    // 将全部语言配置注册到 textmate 中，但是还不能直接使用
    for (const grammarProvider of languageContributions) {
      try {
        grammarProvider.registerTextmateLanguage(textmateRegistry)
      } catch (err) {
        console.error(err)
      }
    }
    const onigLib = Promise.resolve({
      createOnigScanner,
      createOnigString
    })

    // 初始化一个 textmate 注册器，各个语言挂载用
    const grammarRegistry = new Registry({
      onigLib,
      loadGrammar: async (scopeName: string) => {
        const provider = textmateRegistry.getProvider(scopeName)
        if (provider) {
          const definition = await provider.getGrammarDefinition()
          let rawGrammar: IRawGrammar
          if (typeof definition.content === 'string') {
            rawGrammar = parseRawGrammar(definition.content, definition.format === 'json' ? 'grammar.json' : 'grammar.plist')
          } else {
            rawGrammar = definition.content as IRawGrammar
          }
          return rawGrammar
        }
        return undefined
      },
      getInjections: (scopeName: string) => {
        const provider = textmateRegistry.getProvider(scopeName)
        if (provider && provider.getInjections) {
          return provider.getInjections(scopeName)
        }
        return []
      }
    })

    // 激活语言支持
    const _activatedLanguages = new Set<string>()
    const activateLanguage = async (languageId: string): Promise<void> => {
      // 缓存已经打开的语言
      if (_activatedLanguages.has(languageId)) return
      _activatedLanguages.add(languageId)
      // 看 textmate 是否注册了对应的语法
      const scopeName = textmateRegistry.getScope(languageId)
      if (!scopeName) return
      // 看 textmate 是否提供了了对应的 provider
      const provider = textmateRegistry.getProvider(scopeName)
      if (!provider) return
      // 获取语法配置
      const configuration = textmateRegistry.getGrammarConfiguration(languageId)
      const initialLanguage = monaco.languages.getEncodedLanguageId(languageId)
      await onigLib
      try {
        // 实例化一个语法分析器
        const grammar = await grammarRegistry.loadGrammarWithConfiguration(scopeName, initialLanguage, configuration)
        const options = configuration.tokenizerOption ? configuration.tokenizerOption : {}
        // 将语法分析器挂载到 monaco-editor 提供解析服务
        if (grammar !== null) {
          monaco.languages.setTokensProvider(languageId, createTextmateTokenizer(grammar, options))
          const myTokenizer = createTextmateTokenizer(grammar, options)
          console.log(myTokenizer.tokenize('import os', new TokenizerState(INITIAL)))
        } else {
          console.error('grammar not found')
        }
      } catch (error) {
        console.warn('No grammar for this language id ' + languageId)
        console.warn(error)
      }
      console.log('开启语言 ' + languageId + ' 支持')
    }

    // 在用到对应语言才会激活对应的语言
    for (const { id } of monaco.languages.getLanguages()) {
      monaco.languages.onLanguage(id, () => activateLanguage(id))
    }

    monaco.editor.defineTheme('own-vs-dark', vsDark)

    console.log(vsDark)

    const breakpointClassName = 'monaco-editor-breakpoint'
    const shadowBreakpointClassName = 'monaco-editor-breakpoint-shadow'
    console.log('mounted')
    new Promise<void>((resolve, reject) => {
      this.editor = monaco.editor.create(this.$refs.editor as HTMLElement, this.editorOption)
      resolve()
    }).then(() => {
      console.log('set theme')
      monaco.editor.setTheme('own-vs-dark')
    })

    // for lint service
    // install the service
    MonacoServices.install()

    // create websocket
    const url = this.createUrl('localhost', 3000, '/')
    const webSocket = new WebSocket(url)

    // define the connection(websocket) to the language server
    webSocket.onopen = () => {
      const socket = toSocket(webSocket)
      const reader = new WebSocketMessageReader(socket)
      const writer = new WebSocketMessageWriter(socket)
      const languageClient = this.createLanguageClient({ reader, writer })
      languageClient.start()
      reader.onClose(() => languageClient.stop())
    }

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
    this.editor.onMouseLeave(() => {
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

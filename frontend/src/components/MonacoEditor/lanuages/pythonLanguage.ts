import * as monaco from 'monaco-editor/esm/vs/editor/editor.api'
import { LanguageGrammarDefinitionContribution, GrammarDefinition, TextmateRegistry } from '../textmate'

export class PythonContribution implements LanguageGrammarDefinitionContribution {
  readonly id = 'python'
  readonly scopeName = 'source.python'
  registerTextmateLanguage (registry: TextmateRegistry): void {
    monaco.languages.register({
      id: this.id,
      extensions: ['.py'],
      aliases: ['py'],
      mimetypes: ['text/html', 'text/x-jshtm', 'text/template', 'text/ng-template']
    })
    monaco.languages.setLanguageConfiguration(this.id, {
      // eslint-disable-next-line
      wordPattern: /(-?\d*\.\d\w*)|([^\`\~\!\@\$\^\&\*\(\)\=\+\[\{\]\}\\\|\;\:\'\"\,\.\<\>\/\s]+)/g,
      comments: {
        blockComment: ['\'\'\'', '\'\'\'']
      },
      brackets: [
        ['{', '}'],
        ['(', ')']
      ],
      autoClosingPairs: [
        { open: '{', close: '}' },
        { open: '[', close: ']' },
        { open: '(', close: ')' },
        { open: '"', close: '"' },
        { open: '\'', close: '\'' }
      ],
      surroundingPairs: [
        { open: '"', close: '"' },
        { open: '\'', close: '\'' },
        { open: '{', close: '}' },
        { open: '[', close: ']' },
        { open: '(', close: ')' }
      ],
      onEnterRules: [
        {
          beforeText: /:/,
          action: { indentAction: monaco.languages.IndentAction.Indent }
        }
      ],
      folding: {
        // markers: {
        //   start: /^\s*<!--\s*#region\b.*-->/,
        //   end: /^\s*<!--\s*#endregion\b.*-->/
        // }
      }
    })
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const grammar = require('./python.tmLanguage.json')
    registry.registerTextmateGrammarScope(this.scopeName, {
      async getGrammarDefinition (): Promise<GrammarDefinition> {
        console.log('register python grammar')
        console.log(grammar)
        return {
          format: 'json',
          content: grammar
        }
      }
    })
    registry.mapLanguageIdToTextmateGrammar(this.id, this.scopeName)
  }
}

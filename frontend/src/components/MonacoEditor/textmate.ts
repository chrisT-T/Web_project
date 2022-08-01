import { INITIAL, StackElement, IGrammar, IGrammarConfiguration } from 'vscode-textmate'
import * as monaco from 'monaco-editor'

// https://github.com/eclipse-theia/theia/blob/70466bb4b7283187b019defec095f8dea42d47c6/packages/core/src/common/disposable.ts
export interface Disposable {
  /**
   * Dispose this object.
   */
  dispose(): void;
}

// eslint-disable-next-line @typescript-eslint/no-namespace
export namespace Disposable {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  export function is (arg: any): arg is Disposable {
    return !!arg && typeof arg === 'object' && 'dispose' in arg && typeof arg.dispose === 'function'
  }
  export function create (func: () => void): Disposable {
    return { dispose: func }
  }
  /** Always provides a reference to a new disposable. */
  export declare const NULL: Disposable
}

/**
 * Ensures that every reference to {@link Disposable.NULL} returns a new object,
 * as sharing a disposable between multiple {@link DisposableCollection} can have unexpected side effects
 */
Object.defineProperty(Disposable, 'NULL', {
  configurable: false,
  enumerable: true,
  get (): Disposable {
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    return { dispose: () => { } }
  }
})

export function disposableTimeout (...args: Parameters<typeof setTimeout>): Disposable {
  const handle = setTimeout(...args)
  return { dispose: () => clearTimeout(handle) }
}

// https://github.com/eclipse-theia/theia/blob/master/packages/monaco/src/browser/textmate/textmate-tokenizer.ts

export class TokenizerState implements monaco.languages.IState {
  constructor (public readonly ruleStack: StackElement) {
    this.ruleStack = ruleStack
  }

  clone (): monaco.languages.IState {
    return new TokenizerState(this.ruleStack)
  }

  equals (other: monaco.languages.IState): boolean {
    return other instanceof TokenizerState && (other === this || other.ruleStack === this.ruleStack)
  }
}

/**
 * Options for the TextMate tokenizer.
 */
export interface TokenizerOption {

  /**
   * Maximum line length that will be handled by the TextMate tokenizer. If the length of the actual line exceeds this
   * limit, the tokenizer terminates and the tokenization of any subsequent lines might be broken.
   *
   * If the `lineLimit` is not defined, it means, there are no line length limits. Otherwise, it must be a positive
   * integer or an error will be thrown.
   */
  lineLimit?: number

}

export function createTextmateTokenizer (grammar: IGrammar, options: TokenizerOption): monaco.languages.TokensProvider {
  if (options.lineLimit !== undefined && (options.lineLimit <= 0 || !Number.isInteger(options.lineLimit))) {
    throw new Error(`The 'lineLimit' must be a positive integer. It was ${options.lineLimit}.`)
  }
  return {
    getInitialState: () => new TokenizerState(INITIAL),
    // tokenizeEncoded (line: string, state: TokenizerState): monaco.languages.IEncodedLineTokens {
    //   console.log('tokenize 1')
    //   if (options.lineLimit !== undefined && line.length > options.lineLimit) {
    //     // Skip tokenizing the line if it exceeds the line limit.
    //     return { endState: state.ruleStack, tokens: new Uint32Array() }
    //   }
    //   const result = grammar.tokenizeLine2(line, state.ruleStack, 500)
    //   console.log(result)
    //   return {
    //     endState: new TokenizerState(result.ruleStack),
    //     tokens: result.tokens
    //   }
    // },
    tokenize (line: string, state: TokenizerState): monaco.languages.ILineTokens {
      console.log('tokenize 2')
      if (options.lineLimit !== undefined && line.length > options.lineLimit) {
        // Skip tokenizing the line if it exceeds the line limit.
        return { endState: state.ruleStack, tokens: [] }
      }
      const result = grammar.tokenizeLine(line, state.ruleStack, 500)
      console.log(result.tokens.map(t => ({
        startIndex: t.startIndex,
        scopes: t.scopes.reverse().join(' ')
      })))
      return {
        endState: new TokenizerState(result.ruleStack),
        tokens: result.tokens.map(t => ({
          startIndex: t.startIndex,
          scopes: t.scopes.reverse().join(' ')
        }))
      }
    }
  }
}

// https://github.com/eclipse-theia/theia/blob/master/packages/monaco/src/browser/textmate/textmate-registry.ts
export interface TextmateGrammarConfiguration extends IGrammarConfiguration {

  /**
   * Optional options to further refine the tokenization of the grammar.
   */
  readonly tokenizerOption?: TokenizerOption

}

export interface GrammarDefinition {
  format: 'json' | 'plist'
  content: object | string
  location?: string
}

export interface GrammarDefinitionProvider {
  getGrammarDefinition(): Promise<GrammarDefinition>
  getInjections?(scopeName: string): string[]
}

export class TextmateRegistry {
  protected readonly scopeToProvider = new Map<string, GrammarDefinitionProvider[]>()
  protected readonly languageToConfig = new Map<string, TextmateGrammarConfiguration[]>()
  protected readonly languageIdToScope = new Map<string, string[]>()

  get languages (): IterableIterator<string> {
    return this.languageIdToScope.keys()
  }

  registerTextmateGrammarScope (scope: string, provider: GrammarDefinitionProvider): Disposable {
    const providers = this.scopeToProvider.get(scope) || []
    const existingProvider = providers[0]
    if (existingProvider) {
      Promise.all([existingProvider.getGrammarDefinition(), provider.getGrammarDefinition()]).then(([a, b]) => {
        if (a.location !== b.location || (!a.location && !b.location)) {
          console.warn(`a registered grammar provider for '${scope}' scope is overridden`)
        }
      })
    }
    providers.unshift(provider)
    this.scopeToProvider.set(scope, providers)
    return Disposable.create(() => {
      const index = providers.indexOf(provider)
      if (index !== -1) {
        providers.splice(index, 1)
      }
    })
  }

  getProvider (scope: string): GrammarDefinitionProvider | undefined {
    const providers = this.scopeToProvider.get(scope)
    return providers && providers[0]
  }

  mapLanguageIdToTextmateGrammar (languageId: string, scope: string): Disposable {
    const scopes = this.languageIdToScope.get(languageId) || []
    const existingScope = scopes[0]
    if (typeof existingScope === 'string') {
      console.warn(`'${languageId}' language is remapped from '${existingScope}' to '${scope}' scope`)
    }
    scopes.unshift(scope)
    this.languageIdToScope.set(languageId, scopes)
    return Disposable.create(() => {
      const index = scopes.indexOf(scope)
      if (index !== -1) {
        scopes.splice(index, 1)
      }
    })
  }

  getScope (languageId: string): string | undefined {
    const scopes = this.languageIdToScope.get(languageId)
    return scopes && scopes[0]
  }

  getLanguageId (scope: string): string | undefined {
    for (const languageId of this.languageIdToScope.keys()) {
      if (this.getScope(languageId) === scope) {
        return languageId
      }
    }
    return undefined
  }

  registerGrammarConfiguration (languageId: string, config: TextmateGrammarConfiguration): Disposable {
    const configs = this.languageToConfig.get(languageId) || []
    const existingConfig = configs[0]
    if (existingConfig) {
      console.warn(`a registered grammar configuration for '${languageId}' language is overridden`)
    }
    configs.unshift(config)
    this.languageToConfig.set(languageId, configs)
    return Disposable.create(() => {
      const index = configs.indexOf(config)
      if (index !== -1) {
        configs.splice(index, 1)
      }
    })
  }

  getGrammarConfiguration (languageId: string): TextmateGrammarConfiguration {
    const configs = this.languageToConfig.get(languageId)
    return (configs && configs[0]) || {}
  }
}

// 语法支持的统一接口
export interface LanguageGrammarDefinitionContribution {
  registerTextmateLanguage(registry: TextmateRegistry): void;
}

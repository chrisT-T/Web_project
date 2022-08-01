const { defineConfig } = require('@vue/cli-service')
const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin')
module.exports = defineConfig({
  transpileDependencies: true,
  configureWebpack: {
    experiments: {
      asyncWebAssembly: true,
      syncWebAssembly: true
    },
    plugins: [
      new MonacoWebpackPlugin({
        languages: []
      })
    ],
    node: {
      global: false,
      __filename: false,
      __dirname: false
    },
    resolve: {
      fallback: {
        path: false
      }
    }
    // module: {
    //   rules: [
    //     {
    //       test: /\.wasm$/,
    //       loaders: ['wasm-loader']
    //     }
    //   ]
    // }
  }
})

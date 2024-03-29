const AutoImport = require('unplugin-auto-import/webpack')
const Components = require('unplugin-vue-components/webpack')
const { ElementPlusResolver } = require('unplugin-vue-components/resolvers')
const { defineConfig } = require('@vue/cli-service')
const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin')
module.exports = {
  transpileDependencies: true,
  outputDir: './dist',
  // 和webpapck属性完全一致，最后会进行合并
  configureWebpack: {
    resolve: {
      alias: {
        components: '@/components'
      },
      fallback: {
        path: false
      }
    },
    // 配置webpack自动按需引入element-plus，
    plugins: [
      new MonacoWebpackPlugin({
        languages: ['python']
      }),
      AutoImport({
        resolvers: [ElementPlusResolver()]
      }),
      Components({
        resolvers: [ElementPlusResolver()]
      })
    ]
  },
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        ws: true,
        changeOrigin: true
      },
      '/pdb': {
        target: 'http://localhost:5000',
        ws: true,
        changeOrigin: true
      },
      '/pty': {
        target: 'http://localhost:5000',
        ws: true,
        changeOrigin: true
      },
      '/socket.io': {
        target: 'http://localhost:5000',
        ws: true,
        changeOrigin: true
      },
      '/lsp': {
        target: 'ws://localhost:30000',
        ws: true,
        changeOrigin: true,
        pathRewrite: {
          '^/lsp': '/'
        }
      }
    }
  }
}

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'
import VueAxios from 'vue-axios'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const app = createApp(App)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(VueAxios, axios)

app.directive('focus', (el) => {
  el.querySelector('input').focus()
})

app
  .use(store)
  .use(router)
  .use(ElementPlus, { size: 'small', zIndex: 3000 })
  .mount('#app')

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'
import VueAxios from 'vue-axios'

const app = createApp(App)
  .use(VueAxios, axios)

app.directive('focus', (el, binding) => {
  if (binding.value) {
    el.focus()
  }
})

app
  .use(store)
  .use(router)
  .use(ElementPlus, { size: 'small', zIndex: 3000 })
  .mount('#app')

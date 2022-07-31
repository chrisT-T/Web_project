import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'
import VueAxios from 'vue-axios'

createApp(App).use(VueAxios, axios)
createApp(App).use(store).use(router).use(ElementPlus, { size: 'small', zIndex: 3000 }).mount('#app')

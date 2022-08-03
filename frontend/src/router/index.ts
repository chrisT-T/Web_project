import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/index'
  },
  {
    path: '/test/:username',
    name: 'test',
    component: () => import('../views/TestView.vue')
  },
  {
    path: '/index',
    name: 'index',
    component: () => import('../views/IndexView.vue')
  },
  {
    path: '/coding/:username/:projectname',
    name: 'coding',
    component: () => import('../views/CodingView.vue')
  },
  {
    path: '/file',
    name: 'file',
    component: () => import('../components/fileSet.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router

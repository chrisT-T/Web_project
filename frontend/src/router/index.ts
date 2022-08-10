import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/projectmanage/:username',
    name: 'projectmanage',
    component: () => import('../views/ProjectView.vue')
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue')
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

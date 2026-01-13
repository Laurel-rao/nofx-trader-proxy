import { createRouter, createWebHistory } from 'vue-router'
import LogsView from '../views/LogsView.vue'
import ConfigView from '../views/ConfigView.vue'
import StatsView from '../views/StatsView.vue'
import TestView from '../views/TestView.vue'
import WhitelistView from '../views/WhitelistView.vue'

const routes = [
  {
    path: '/',
    redirect: '/logs'
  },
  {
    path: '/logs',
    name: 'Logs',
    component: LogsView
  },
  {
    path: '/config',
    name: 'Config',
    component: ConfigView
  },
  {
    path: '/stats',
    name: 'Stats',
    component: StatsView
  },
  {
    path: '/test',
    name: 'Test',
    component: TestView
  },
  {
    path: '/whitelist',
    name: 'Whitelist',
    component: WhitelistView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router


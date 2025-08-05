import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '@/layout/default.vue'
import HomeView from '@/views/HomeView.vue'
// @ts-ignore
import ClientLogFilterView from '@/views/ClientLogFilterView.vue'
// @ts-ignore
import LogPasteView from '@/views/LogPasteView.vue'
// @ts-ignore
import LogPoolView from '@/views/LogPoolView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'homeLayout',
      component: DefaultLayout,
      children: [
        {
          path: '/',
          name: 'home',
          component: HomeView,
        },
        {
          path: '/clientLogFilter',
          name: 'clientLogFilter',
          component: ClientLogFilterView,
        },
        {
          path: '/log-paste',
          name: 'LogPaste',
          component: LogPasteView,
        },
        {
          path: '/log-pool',
          name: 'LogPool',
          component: LogPoolView,
        },
      ],
    },
  ],
})

export default router

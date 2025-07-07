import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '@/layout/default.vue'
import HomeView from '@/views/HomeView.vue'
import ClilentLogFilterView from '@/views/ClientLogFilterView.vue'

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
          component: ClilentLogFilterView,
        },
      ],
    },
  ],
})

export default router

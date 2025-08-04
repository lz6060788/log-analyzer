import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '@/layout/default.vue'
import HomeView from '@/views/HomeView.vue'
import ClilentLogFilterView from '@/views/ClientLogFilterView.vue'
import LogPasteView from '../views/LogPasteView.vue';
import LogPoolView from '../views/LogPoolView.vue';

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

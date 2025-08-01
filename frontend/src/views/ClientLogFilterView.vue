<script setup>
import statisticPanel from '@/components/clientLogFilter/statisticPanel.vue';
import accountsPanel from '@/components/clientLogFilter/accountsPanel.vue';
import fundPanel from '@/components/clientLogFilter/fundPanel.vue';
import positionPanel from '@/components/clientLogFilter/positionPanel.vue';
import orderPanel from '@/components/clientLogFilter/orderPanel.vue';
import tradePanel from '@/components/clientLogFilter/tradePanel.vue';
import ipoPanel from '@/components/clientLogFilter/ipoPanel.vue';
import finablePanel from '@/components/clientLogFilter/finablePanel.vue';
import basketPanel from '@/components/clientLogFilter/basketPanel.vue';
import algorithmPanel from '@/components/clientLogFilter/algorithmPanel.vue';
import ConditionPanel from '@/components/clientLogFilter/conditionPanel.vue';
import filterPanel from '@/components/clientLogFilter/filterPanel.vue';
import floatingNavigation from '@/components/common/FloatingNavigation.vue';

const items = [
  { title: '汇总请求统计' },
  { title: '账户请求统计' },
  { title: '资金请求统计' },
  { title: '持仓请求统计' },
  { title: '委托请求统计' },
  { title: '成交请求统计' },
  { title: '新股申购请求统计' },
  { title: '可融资标的券请求统计' },
  { title: '篮子/集中请求统计' },
  { title: '算法请求统计' },
  { title: '条件单请求统计' },
  { title: '日志过滤器' },
]
</script>

<template>
  <teleport to="#container-wrapper">
    <floating-navigation title="导航窗口" :navigationItems="items"></floating-navigation>
  </teleport>
  <statistic-panel></statistic-panel>
  <accounts-panel></accounts-panel>
  <fund-panel></fund-panel>
  <position-panel></position-panel>
  <order-panel></order-panel>
  <trade-panel></trade-panel>
  <ipo-panel></ipo-panel>
  <finable-panel></finable-panel>
  <basket-panel></basket-panel>
  <algorithm-panel></algorithm-panel>
  <condition-panel></condition-panel>
  <filter-panel></filter-panel>
</template>


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
</script>

<template>
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


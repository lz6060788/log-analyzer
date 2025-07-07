<script setup>
import { ref } from 'vue';
import { useClientLogAnalyser } from '@/composable/clientLog';
import dataPanel from '@/components/common/dataPanel.vue';
import commonTable from '@/components/common/commonTable';
import { useClientLogStore } from '@/store/clientLog'
import { storeToRefs } from 'pinia';

const clientLogStore = useClientLogStore();
const { fetchStatisticList } = storeToRefs(clientLogStore)
const { getStatisticData } = useClientLogAnalyser();

const isLoadingStatisticData = ref(false);
const refreshStatisticData = async () => {
  isLoadingStatisticData.value = true;
  await getStatisticData();
  isLoadingStatisticData.value = false;
};
</script>

<template>
  <dataPanel title="汇总请求统计">
    <template #actions>
      <el-button @click="refreshStatisticData" :loading="isLoadingStatisticData" size='small' type="primary">刷新</el-button>
    </template>
    <template #data>
      <common-table :data="fetchStatisticList"></common-table>
    </template>
  </dataPanel>
</template>

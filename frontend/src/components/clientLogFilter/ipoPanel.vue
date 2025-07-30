<script setup>
import { computed, ref } from 'vue';
import { useClientLogAnalyser } from '@/composable/clientLog';
import dataPanel from '@/components/common/dataPanel.vue';
import commonTable from '@/components/common/commonTable';
import { useClientLogStore } from '@/store/clientLog'
import { storeToRefs } from 'pinia';

const clientLogStore = useClientLogStore();
const { ipoFetchMap, ipoLotteryFetchMap } = storeToRefs(clientLogStore)
const { getIpoLogs, getIpoLotteryLogs } = useClientLogAnalyser();

const isLoadingData = ref(false);
const refreshData = async () => {
  reset();
  isLoadingData.value = true;
  await getIpoLogs();
  await getIpoLotteryLogs();
  isLoadingData.value = false;
};

const accountList = computed(() => {
  return Array.from(new Set([
    ...ipoFetchMap.value.map(item => item.fund),
    ...ipoLotteryFetchMap.value.map(item => item.fund)
  ]))
});
const currentAccount = ref('');

const ipoFetchTableData = computed(() => !currentAccount.value ? ipoFetchMap.value : ipoFetchMap.value.filter(item => item.fund === currentAccount.value))
const ipoLotteryFetchTableData = computed(() => !currentAccount.value ? ipoLotteryFetchMap.value : ipoLotteryFetchMap.value.filter(item => item.fund === currentAccount.value))

const reset = () => {
  currentAccount.value = '';
}
</script>

<template>
  <dataPanel title="新股申购请求统计">
    <template #actions>
        <el-select v-model="currentAccount" size="small" style="width: 200px;" placeholder="请选择账户" clearable @change="currentTime = ''"> 
          <el-option v-for="item in accountList" :key="item" :label="item" :value="item"></el-option>
        </el-select>
        <el-button @click="refreshData" :loading="isLoadingData" size='small' type="primary">刷新</el-button>
    </template>
    <template #data>
      <p class="my-2 font-bold">额度查询</p>
      <common-table :data="ipoFetchTableData">
        <template #req_id="{ row }">
          <copy-text :text="row.req_id"></copy-text>
        </template>
      </common-table>
      <p class="my-2 font-bold">中签查询</p>
      <common-table :data="ipoLotteryFetchMap">
        <template #req_id="{ row }">
          <copy-text :text="row.req_id"></copy-text>
        </template>
      </common-table>
    </template>
  </dataPanel>
</template>

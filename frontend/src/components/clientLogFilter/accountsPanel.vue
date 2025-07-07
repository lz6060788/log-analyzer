<script setup>
import { computed, ref } from 'vue';
import { useClientLogAnalyser } from '@/composable/clientLog';
import dataPanel from '@/components/common/dataPanel.vue';
import commonTable from '@/components/common/commonTable';
import copyText from '@/components/common/copyText.vue';
import { useClientLogStore } from '@/store/clientLog'
import { storeToRefs } from 'pinia';

const clientLogStore = useClientLogStore();
const { accountsFetchMap } = storeToRefs(clientLogStore)

const { getAccountsLogs } = useClientLogAnalyser();

const isLoadingAccountsData = ref(false);
const accountsFetchTimeList = computed(() => Object.keys(accountsFetchMap.value));
const filterAccountFetchTime = ref('');
const accountList = computed(() => accountsFetchMap.value[filterAccountFetchTime.value] || [])
const refreshAccounstData = async () => {
  isLoadingAccountsData.value = true;
  await getAccountsLogs() || [];
  filterAccountFetchTime.value = accountsFetchTimeList.value[0];
  isLoadingAccountsData.value = false;
};
</script>

<template>
  <dataPanel title="账户请求统计">
    <template #actions>
      <el-button @click="refreshAccounstData" :loading="isLoadingAccountsData" size='small' type="primary">刷新</el-button>
      <el-select v-model="filterAccountFetchTime" size="small" style="width: 200px;" placeholder="请选择时间"> 
        <el-option v-for="item in accountsFetchTimeList" :key="item" :label="item" :value="item">
        </el-option>
      </el-select>
    </template>
    <template #data>
      <common-table :data="accountList">
        <template #fund_token="{ row }">
          <copy-text :text="row.fund_token"></copy-text>
        </template>
      </common-table>
    </template>
  </dataPanel>
</template>

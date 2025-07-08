<script setup>
import { computed, ref } from 'vue';
import { useClientLogAnalyser } from '@/composable/clientLog';
import dataPanel from '@/components/common/dataPanel.vue';
import commonTable from '@/components/common/commonTable';
import { useClientLogStore } from '@/store/clientLog'
import { storeToRefs } from 'pinia';

const clientLogStore = useClientLogStore();
const { fundFetchMap } = storeToRefs(clientLogStore)
const { getFundLogs } = useClientLogAnalyser();

const isLoadingData = ref(false);
const refreshFundLogs = async () => {
  currentAccount.value = '';
  isLoadingData.value = true;
  await getFundLogs();
  isLoadingData.value = false;
};

const tabs = [
  { label: '普通', value: 'normal' },
  { label: '信用', value: 'rzrq' },
  { label: '港股通', value: 'ggt' },
  { label: '异常', value: 'failed' },
]
const tab = ref('normal');

const currentTabMap =  computed(() => {
  console.log('fundFetchMap[tab.value]', fundFetchMap.value?.[tab.value])
  return fundFetchMap.value?.[tab.value] || {}
})
const accountList = computed(() => Object.keys(currentTabMap.value));
const currentAccount = ref('');
const currentTableData = computed(() => {
  console.log('urrentTabMap.value[currentAccount.value]', currentTabMap.value[currentAccount.value])
  if (!currentAccount.value) {
    return []
  }
  return currentTabMap.value[currentAccount.value]
})
</script>

<template>
  <dataPanel title="资金请求统计">
    <template #actions>
        <el-radio-group v-model="tab" size="small">
          <el-radio-button v-for="item in tabs" :key="item.value" :label="item.value">{{ item.label }}</el-radio-button>
        </el-radio-group>
        <el-select v-model="currentAccount" size="small" style="width: 200px;" placeholder="请选择账户"> 
          <el-option v-for="item in accountList" :key="item" :label="item" :value="item"></el-option>
        </el-select>
        <el-button @click="refreshFundLogs" :loading="isLoadingData" size='small' type="primary">刷新</el-button>
    </template>
    <template #data>
      <common-table :data="currentTableData"></common-table>
    </template>
  </dataPanel>
</template>

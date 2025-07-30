<script setup>
import { computed, ref } from 'vue';
import { useClientLogAnalyser } from '@/composable/clientLog';
import dataPanel from '@/components/common/dataPanel.vue';
import commonTable from '@/components/common/commonTable';
import { useClientLogStore } from '@/store/clientLog'
import { storeToRefs } from 'pinia';

const clientLogStore = useClientLogStore();
const { tradeFetchMap, tradeSummary } = storeToRefs(clientLogStore)
const { getTradeLogs, getTradeSummary } = useClientLogAnalyser();

const isLoadingData = ref(false);
const refreshData = async () => {
  reset();
  isLoadingData.value = true;
  await getTradeLogs();
  getTradeSummary();
  isLoadingData.value = false;
};

const tabs = [
  { label: '普通', value: 'normal' },
  { label: '信用', value: 'rzrq' },
  { label: '港股通', value: 'ggt' },
]
const tab = ref('normal');

const currentTabMap =  computed(() => {
  return tradeFetchMap.value?.[tab.value] || {}
})
const accountList = computed(() => Object.keys(currentTabMap.value));
const currentAccount = ref('');
const currentTimeMap = computed(() => {
  return currentTabMap.value?.[currentAccount.value] || {};
})

const timeList = computed(() => Object.keys(currentTimeMap.value));
const currentTime = ref('');
const currentTableData = computed(() => {
  if (!currentTime.value) {
    return []
  }
  return currentTimeMap.value[currentTime.value]
})

const reset = () => {
  currentAccount.value = '';
  currentTime.value = '';
}
</script>

<template>
  <dataPanel title="成交请求统计">
    <template #actions>
        <el-radio-group v-model="tab" size="small" @change="reset">
          <el-radio-button v-for="item in tabs" :key="item.value" :value="item.value">{{ item.label }}</el-radio-button>
        </el-radio-group>
        <el-select v-model="currentAccount" size="small" style="width: 200px;" placeholder="请选择账户" @change="currentTime = ''"> 
          <el-option v-for="item in accountList" :key="item" :label="item" :value="item"></el-option>
        </el-select>
        <el-select v-model="currentTime" size="small" style="width: 200px;" placeholder="请选择请求时间"> 
          <el-option v-for="item in timeList" :key="item" :label="item" :value="item"></el-option>
        </el-select>
        <el-button @click="refreshData" :loading="isLoadingData" size='small' type="primary">刷新</el-button>
    </template>
    <template #data>
      <common-table :data="currentTableData"></common-table>
      <div class="mt-1">
        <p class="leading-8">港股通账户数：{{ tradeSummary.ggt_accounts }}</p>
        <p class="leading-8">普通账户数：{{ tradeSummary.normal_accounts }}</p>
        <p class="leading-8">融资融券账户数：{{ tradeSummary.rzrq_accounts }}</p>
        <p class="leading-8">总港股通请求数：{{ tradeSummary.total_ggt_queries }}</p>
        <p class="leading-8">总普通请求数：{{ tradeSummary.total_normal_queries }}</p>
        <p class="leading-8">总融资融券请求数：{{ tradeSummary.total_rzrq_queries }}</p>
      </div>
    </template>
  </dataPanel>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useClientLogAnalyser } from '@/composable/clientLog';
import dataPanel from '@/components/common/dataPanel.vue';
import commonTable from '@/components/common/commonTable';
import { useClientLogStore } from '@/store/clientLog'
import { storeToRefs } from 'pinia';

const clientLogStore = useClientLogStore();
const { finableSecurityMap, finableSecurityFailed } = storeToRefs(clientLogStore)
const { getFinableSecurityData, getFinableSecurityFailed } = useClientLogAnalyser();

const isLoadingData = ref(false);
const refreshData = async () => {
  reset();
  isLoadingData.value = true;
  await getFinableSecurityData();
  await getFinableSecurityFailed();
  isLoadingData.value = false;
  };

const accountList = computed(() => Object.keys(finableSecurityMap.value));
const currentAccount = ref('');
const currentTimeMap = computed(() => {
  return finableSecurityMap.value?.[currentAccount.value] || {};
})

const timeList = computed(() => Object.keys(currentTimeMap.value));
const currentTime = ref('');
const currentTableData = computed(() => {
  if (!currentTime.value) {
    return []
  }
  return currentTimeMap.value[currentTime.value]
})

// 按MarketName进行分类统计
const marketNameStatistics = computed(() => {
  if (!currentTableData.value || currentTableData.value.length === 0) {
    return []
  }

  const statistics = {}

  currentTableData.value.forEach(item => {
    const marketName = item.MarketName || '未知市场'
    if (!statistics[marketName]) {
      statistics[marketName] = 0
    }
    statistics[marketName]++
  })

  // 转换为数组格式，便于显示
  return Object.entries(statistics).map(([marketName, count]) => ({
    marketName,
    count
  })).sort((a, b) => b.count - a.count) // 按数量降序排列
})

const search = ref('');
const filteredTableData = computed(() => {
  if (!search.value) {
    return currentTableData.value
  }
  return currentTableData.value.filter(item => item.Symbol.includes(search.value) || item.SecurityID.includes(search.value))
})

const reset = () => {
  search.value = '';
  currentAccount.value = '';
  currentTime.value = '';
}
</script>

<template>
  <dataPanel title="可融资标的统计">
    <template #actions>
        <el-select v-model="currentAccount" size="small" style="width: 200px;" placeholder="请选择账户" @change="currentTime = ''"> 
          <el-option v-for="item in accountList" :key="item" :label="item" :value="item"></el-option>
        </el-select>
        <el-select v-model="currentTime" size="small" style="width: 200px;" placeholder="请选择请求时间"> 
          <el-option v-for="item in timeList" :key="item" :label="item" :value="item"></el-option>
        </el-select>
        <el-input v-model="search" size="small" placeholder="请输入标的代码或名称检索" style="width: 200px;" />
        <el-button @click="refreshData" :loading="isLoadingData" size='small' type="primary">刷新</el-button>
    </template>
    <template #data>
      <!-- 市场分类统计 -->
      <div v-if="marketNameStatistics.length > 0" class="mb-4">
        <h3 class="font-bold mb-2">市场分类统计</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div
            v-for="stat in marketNameStatistics" 
            :key="stat.marketName"
            class="bg-blue-50 border border-blue-200 rounded-lg p-3"
          >
            <div class="text-sm text-gray-600">{{ stat.marketName }}</div>
            <div class="text-xl font-bold text-blue-600">{{ stat.count }}</div>
          </div>
        </div>
      </div>

      <div class="mb-2 flex items-center">
        <h3 class="font-bold mr-2">可融资标的查询数据</h3>
        <span v-if="currentTableData.length > 0" class="text-sm text-gray-500">
          (总计: {{ currentTableData.length }} 条)
        </span>
      </div>
      <common-table :data="filteredTableData"></common-table>
      <div class="my-2 flex items-center">
        <h3 class="font-bold mr-2">失败请求：</h3>
      </div>
      <common-table :data="finableSecurityFailed"></common-table>
    </template>
  </dataPanel>
</template>

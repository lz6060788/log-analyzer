<script setup>
import { computed, ref } from 'vue';
import { useClientLogAnalyser } from '@/composable/clientLog';
import dataPanel from '@/components/common/dataPanel.vue';
import commonTable from '@/components/common/commonTable';
import { useClientLogStore } from '@/store/clientLog'
import { storeToRefs } from 'pinia';

const clientLogStore = useClientLogStore();
const { algorithmQueryData, newAlgorithmOrder } = storeToRefs(clientLogStore)
const {
  getNewAlgorithmOrder,
  getAlgorithmQueryData,
  getAlgorithmDetail,
  getAlgorithmPushDetail,
  getAlgorithmCode,
} = useClientLogAnalyser();

const isLoadingData = ref(false);
const codeList = ref([]);
const queryNewOrderData = async () => {
  isLoadingData.value = true;
  await getNewAlgorithmOrder();
  codeList.value = await getAlgorithmCode();
  isLoadingData.value = false;
};

const isLoadingAlgorithmQueryData = ref(false);
const queryAlgorithmOrderData = async () => {
  isLoadingAlgorithmQueryData.value = true;
  await getAlgorithmQueryData();
  isLoadingAlgorithmQueryData.value = false;
};
const timeList = computed(() => Object.keys(algorithmQueryData.value));
const currentTime = ref('');
const currentTableData = computed(() => {
  if (!currentTime.value) {
    return []
  }
  return algorithmQueryData.value[currentTime.value] || []
})

const isLoadingDetailData = ref(false);
const instanceid = ref('');
const algorithmInstanceDetail = ref([]);
const instructionPushDetail = ref([]);
const orderPushDetail = ref([]);
const queryAlgorithmDetailData = async () => {
  if (!instanceid.value) {
    ElNotification.error('请输入母单实例ID');
    return;
  }
  algorithmInstanceDetail.value = [];
  instructionPushDetail.value = [];
  orderPushDetail.value = [];
  isLoadingDetailData.value = true;
  algorithmInstanceDetail.value = await getAlgorithmDetail(instanceid.value) || [];
  instructionPushDetail.value = await getAlgorithmPushDetail(instanceid.value, 'twap_instruction') || [];
  orderPushDetail.value = await getAlgorithmPushDetail(instanceid.value, 'twap_order') || [];
  isLoadingDetailData.value = false;
};

const reset = () => {
  // currentAccount.value = '';
  // currentTime.value = '';
}
</script>

<template>
  <dataPanel title="算法请求统计">
    <template #actions>
        <!-- <el-select v-model="currentAccount" size="small" style="width: 200px;" placeholder="请选择账户" @change="currentTime = ''"> 
          <el-option v-for="item in accountList" :key="item" :label="item" :value="item"></el-option>
        </el-select> -->
        <el-button @click="queryNewOrderData" :loading="isLoadingData" size='small' type="primary">查询</el-button>
    </template>
    <template #data>
      <common-table :data="newAlgorithmOrder">
        <template #InstanceID="{ row }">
          <copy-text :text="row.InstanceID"></copy-text>
        </template>
      </common-table>
      <h4 class="font-bold my-2">涉及交易股票列表:</h4>
      <div>
        <span v-for="(item, index) in codeList" :key="item">
          <copy-text :text="item"></copy-text>
          <span v-if="index !== codeList.length - 1">、</span>
        </span>
      </div>
      <div class="flex items-center gap-2 mb-2 mt-4">
        <p class="font-bold text-blue-900">母单请求统计</p>
        <el-select v-model="currentTime" size="small" style="width: 200px;" placeholder="请选择请求时间">
          <el-option v-for="item in timeList" :key="item" :label="item" :value="item"></el-option>
        </el-select>
        <el-button @click="queryAlgorithmOrderData" :loading="isLoadingAlgorithmQueryData" size='small' type="primary">查询</el-button>
      </div>
      <common-table :data="currentTableData">
        <template #inst_id="{ row }">
          <copy-text :text="row.inst_id"></copy-text>
        </template>
      </common-table>
      <div class="flex items-center gap-2 mb-2 mt-4">
        <p class="font-bold text-blue-900">查询算法单详情</p>
        <el-input v-model="instanceid" size="small" style="width: 200px;" placeholder="请输入算法单实例ID" clearable></el-input>
        <el-button @click="queryAlgorithmDetailData" :loading="isLoadingDetailData" size='small' type="primary">查询</el-button>
      </div>
      <div>
        <h4 class="font-bold my-2">母单详情</h4>
        <common-table :data="algorithmInstanceDetail"></common-table>
      </div>
      <div>
        <h4 class="font-bold my-2">母单推送详情</h4>
        <common-table :data="instructionPushDetail"></common-table>
      </div>
      <div>
        <h4 class="font-bold my-2">委托推送详情</h4>
        <common-table :data="orderPushDetail"></common-table>
      </div>
    </template>
  </dataPanel>
</template>

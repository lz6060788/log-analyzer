<script setup>
import { computed, ref } from 'vue';
import { useClientLogAnalyser } from '@/composable/clientLog';
import dataPanel from '@/components/common/dataPanel.vue';
import commonTable from '@/components/common/commonTable';
import { useClientLogStore } from '@/store/clientLog'
import { storeToRefs } from 'pinia';

const clientLogStore = useClientLogStore();
const { basketSummary, basketOrderDetail, basketQueryData } = storeToRefs(clientLogStore)
const {
  getBasketSummaryData,
  getBasketInstanceDetail,
  getBasketOrderDetail,
  getBasketQueryData,
  getBasketInitReqs
} = useClientLogAnalyser();

const isLoadingData = ref(false);
const quereySummaryData = async () => {
  isLoadingData.value = true;
  await getBasketSummaryData(tab.value, fund.value, stockcode.value);
  isLoadingData.value = false;
};
const singleorderSuccessTableData = computed(() => {
  return basketSummary.value.singleorder_success || []
})
const singleorderFailedTableData = computed(() => {
  return basketSummary.value.singleorder_failed || []
})
const singleorderCancelTableData = computed(() => {
  return basketSummary.value.singleorder_cancel || []
})
const basketorderTableData = computed(() => {
  return basketSummary.value.basketorder || []
})
const basketorderOpTableData = computed(() => {
  return basketSummary.value.basketorder_op || []
})
const distinctSecurityList = computed(() => {
  return basketSummary.value.distinct_security_list || []
})

const tabs = [
  { label: '全部', value: '全部' },
  { label: '港股通', value: '港股通' },
  { label: '闪电下单', value: '闪电下单' },
]
const tab = ref('全部');
const fund = ref('');
const stockcode = ref('');

const isLoadingBasketQueryData = ref(false);
const queryBasketOrderData = async () => {
  isLoadingBasketQueryData.value = true;
  await getBasketQueryData();
  isLoadingBasketQueryData.value = false;
};
const timeList = computed(() => Object.keys(basketQueryData.value));
const currentTime = ref('');
const currentTableData = computed(() => {
  if (!currentTime.value) {
    return []
  }
  return basketQueryData.value[currentTime.value]
})

const isLoadingDetailData = ref(false);
const instanceid = ref('');
const basketInstanceDetail = ref({});
const subOrderDetail = ref([]);
const queryBasketDetailData = async () => {
  if (!instanceid.value) {
    ElNotification.error('请输入母单实例ID');
    return;
  }
  basketInstanceDetail.value = {};
  isLoadingDetailData.value = true;
  basketInstanceDetail.value = await getBasketInstanceDetail(instanceid.value),
  subOrderDetail.value = await getBasketOrderDetail(instanceid.value),
  isLoadingDetailData.value = false;
};
const basketInstanceDetailForRequestParams = computed(() => {
  return basketInstanceDetail.value.the_create || []
})
const basketInstanceDetailForOrder = computed(() => {
  return basketInstanceDetail.value.basketorder_detail || []
})


const reset = () => {
  // currentAccount.value = '';
  // currentTime.value = '';
}
</script>

<template>
  <dataPanel title="篮子/集中请求统计">
    <template #actions>
        <el-radio-group v-model="tab" size="small" @change="reset">
          <el-radio-button v-for="item in tabs" :key="item.value" :value="item.value">{{ item.label }}</el-radio-button>
        </el-radio-group>
        <el-input v-model="fund" size="small" style="width: 200px;" placeholder="筛选账户" clearable></el-input>
        <el-input v-model="stockcode" size="small" style="width: 200px;" placeholder="筛选股票代码" clearable></el-input>
        <!-- <el-select v-model="currentAccount" size="small" style="width: 200px;" placeholder="请选择账户" @change="currentTime = ''"> 
          <el-option v-for="item in accountList" :key="item" :label="item" :value="item"></el-option>
        </el-select>
        <el-select v-model="currentTime" size="small" style="width: 200px;" placeholder="请选择请求时间"> 
          <el-option v-for="item in timeList" :key="item" :label="item" :value="item"></el-option>
        </el-select> -->
        <el-button @click="quereySummaryData" :loading="isLoadingData" size='small' type="primary">查询</el-button>
    </template>
    <template #data>
      <h4 class="font-bold mb-2">单户委托成功请求</h4>
      <common-table :data="singleorderSuccessTableData"></common-table>
      <h4 class="font-bold my-2">单户委托失败请求</h4>
      <common-table :data="singleorderFailedTableData"></common-table>
      <h4 class="font-bold my-2">单户撤单请求</h4>
      <common-table :data="singleorderCancelTableData"></common-table>
      <h4 class="font-bold my-2">母单委托请求</h4>
      <common-table :data="basketorderTableData">
        <template #instanceid="{ row }">
          <copy-text :text="row.instanceid"></copy-text>
        </template>
      </common-table>
      <h4 class="font-bold my-2">母单操作请求</h4>
      <common-table :data="basketorderOpTableData"></common-table>
      <h4 class="font-bold my-2">多户交易股票列表:</h4>
      <!-- 不使用表格展示 -->
      <div>
        <span v-for="(item, index) in distinctSecurityList" :key="item">
          <copy-text :text="item"></copy-text>
          <span v-if="index !== distinctSecurityList.length - 1">、</span>
        </span>
      </div>
      <div class="flex items-center gap-2 mb-2 mt-4">
        <p class="font-bold text-blue-900">按请求时间检索母单请求</p>
        <el-select v-model="currentTime" size="small" style="width: 200px;" placeholder="请选择请求时间"> 
          <el-option v-for="item in timeList" :key="item" :label="item" :value="item"></el-option>
        </el-select>
        <el-button @click="queryBasketOrderData" :loading="isLoadingBasketQueryData" size='small' type="primary">查询</el-button>
      </div>
      <common-table :data="currentTableData">
        <template #InstanceID="{ row }">
          <copy-text :text="row.InstanceID"></copy-text>
        </template>
      </common-table>
      <div class="flex items-center gap-2 mb-2 mt-4">
        <p class="font-bold text-blue-900">查询母/子单详情</p>
        <el-input v-model="instanceid" size="small" style="width: 200px;" placeholder="请输入母单实例ID" clearable></el-input>
        <el-button @click="queryBasketDetailData" :loading="isLoadingDetailData" size='small' type="primary">查询</el-button>
      </div>
      <!-- 以下一块区域用于显示请求时间、应答时间等信息，需要在同一行中展示 -->
      <div class="flex items-center gap-2 mb-2 mt-4">
        <p class="text-sm">请求时间</p>
        <p>{{ basketInstanceDetail.req_time }}</p>
      </div>
      <div class="flex items-center gap-2 mb-2 mt-4">
        <p class="text-sm">应答时间</p>
        <p>{{ basketInstanceDetail.rsp_time }}</p>
      </div>
      <div>
        <h4 class="font-bold my-2">母单请求参数</h4>
        <common-table :data="basketInstanceDetailForRequestParams"></common-table>
      </div>
      <div>
        <h4 class="font-bold my-2">母单详情</h4>
        <common-table :data="basketInstanceDetailForOrder"></common-table>
      </div>
      <div v-for="(detail, index) in subOrderDetail"  :key="index">
        <h4 class="font-bold my-2">子单详情 - fund: {{ detail[0]?.fundinfo }}  |  fundtoken: <copy-text :text="detail[0]?.fund_token"></copy-text></h4>
        <common-table :data="detail"></common-table>
      </div>
    </template>
  </dataPanel>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useClientLogAnalyser } from '@/composable/clientLog';
import dataPanel from '@/components/common/dataPanel.vue';
import commonTable from '@/components/common/commonTable';
import { useClientLogStore } from '@/store/clientLog'
import { storeToRefs } from 'pinia';
import MonacoEditor from '@/components/common/MonacoEditor.vue';

const clientLogStore = useClientLogStore();
const { conditionSummary, conditionQueryData } = storeToRefs(clientLogStore)
const {
  getConditionSummaryData,
  getConditionInstanceDetailData,
  getConditionOrderDetailData,
  getConditionSecurityOrderDetailData,
  getConditionInitReqsData,
  getConditionQueryData
} = useClientLogAnalyser();

// 新增汇总数据
const isLoadingData = ref(false);
const queryConditionData = async () => {
  isLoadingData.value = true;
  await getConditionSummaryData();
  isLoadingData.value = false;
};
const conditionCreateTableData = computed(() => {
  return conditionSummary.value.create || []
})
const conditionOperationsTableData = computed(() => {
  return conditionSummary.value.info || []
})

// 请求查询
const isLoadingConditionQueryData = ref(false);
const queryConditionOrderData = async () => {
  isLoadingConditionQueryData.value = true;
  await getConditionQueryData();
  isLoadingConditionQueryData.value = false;
};
const timeList = computed(() => Object.keys(conditionQueryData.value));
const currentTime = ref('');
const currentTableData = computed(() => {
  if (!currentTime.value) {
    return []
  }
  return conditionQueryData.value[currentTime.value]
})

// 母单详情
const fund = ref('');
const isLoadingDetailData = ref(false);
const conditionInstanceInstanceId = ref('');
const conditionInstanceDetail = ref({});
const conditionSecurityOrderDetail = ref({});
const queryConditionDetailData = async () => {
  if (!conditionInstanceInstanceId.value) {
    ElNotification.error('请输入母单实例ID');
    return;
  }
  conditionInstanceDetail.value = {};
  isLoadingDetailData.value = true;
  conditionInstanceDetail.value = await getConditionInstanceDetailData(conditionInstanceInstanceId.value),
  isLoadingDetailData.value = false;
};
// 母单详情数据
const conditionInstanceDetailForConditionList = computed(() => {
  return conditionInstanceDetail.value.condition_list || []
})
const conditionInstanceDetailForGradeConditionDetail = computed(() => {
  return conditionInstanceDetail.value.df_gradecondition_detail || []
})
const conditionInstanceDetailForFirstPush = computed(() => {
  return conditionInstanceDetail.value.df_gradecondition_first_push || {}
})
const conditionInstanceDetailForOperations = computed(() => {
  return conditionInstanceDetail.value.df_gradecondition_operations || []
})
const conditionInstanceDetailForPushList = computed(() => {
  return conditionInstanceDetail.value.df_gradecondition_push_instruction || []
})
const conditionInstanceDetailForStockList = computed(() => {
  return conditionInstanceDetail.value.gradecondition_stocks || []
})
const conditionInstanceDetailForRequestParams = computed(() => {
  return conditionInstanceDetail.value.list_the_create || []
})
const conditionInstanceDetailForModifyInformation = computed(() => {
  return conditionInstanceDetail.value.modify_information || []
})

// 子单详情数据
const isLoadingConditionOrderDetailData = ref(false);
const conditionOrderInstanceId = ref('');
const conditionOrderDetail = ref({});
const queryConditionOrderDetailData = async () => {
  isLoadingConditionOrderDetailData.value = true;
  conditionOrderDetail.value = await getConditionOrderDetailData(conditionOrderInstanceId.value);
  isLoadingConditionOrderDetailData.value = false;
};
const conditionOrderDetailForConditionList = computed(() => {
  return conditionOrderDetail.value.condition_list || []
})
const conditionOrderDetailForGradeConditionDetail = computed(() => {
  return conditionOrderDetail.value.df_grade_condition || []
})

const isLoadingConditionSecurityOrderDetailData = ref(false);
const conditionSecurityOrderInstanceId = ref('');
const queryConditionSecurityOrderDetailData = async () => {
  isLoadingConditionSecurityOrderDetailData.value = true;
  conditionSecurityOrderDetail.value = await getConditionSecurityOrderDetailData(conditionSecurityOrderInstanceId.value, fund.value, stockcode.value);
  isLoadingConditionSecurityOrderDetailData.value = false;
};
// 子单个股详情
const stockcode = ref('');
const conditionSecurityOrderDetailForParams= computed(() => {
  return conditionSecurityOrderDetail.value.condition_params || {}
})
const conditionSecurityOrderDetailForPushList = computed(() => {
  return conditionSecurityOrderDetail.value.df_gradecondition_push_order || []
})
const conditionSecurityOrderDetailForErrorMsgs = computed(() => {
  return conditionSecurityOrderDetail.value.error_msgs || []
})


const reset = () => {
  // currentAccount.value = '';
  // currentTime.value = '';
}
</script>

<template>
  <dataPanel title="条件单请求统计">
    <template #actions>
        <el-button @click="queryConditionData" :loading="isLoadingData" size='small' type="primary">查询</el-button>
    </template>
    <template #data>
      <div>
        <h4 class="font-bold mb-2">当日新增条件单</h4>
        <common-table :data="conditionCreateTableData">
          <template #order_no="{ row }">
            <copy-text :text="row.order_no"></copy-text>
          </template>
        </common-table>
        <h4 class="font-bold my-2">条件单操作请求</h4>
        <common-table :data="conditionOperationsTableData">
          <template #order_no="{ row }">
            <copy-text :text="row.order_no"></copy-text>
          </template>
        </common-table>
        <div class="mb-4">
          <h4 class="font-bold mb-2">推送统计</h4>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div
              class="bg-blue-50 border border-blue-200 rounded-lg p-3"
            >
              <div class="text-sm text-gray-600">母单推送数</div>
              <div class="text-xl font-bold text-blue-600">{{ conditionSummary.instruction_push_length }}</div>
            </div>
            <div
              class="bg-blue-50 border border-blue-200 rounded-lg p-3"
            >
              <div class="text-sm text-gray-600">子单推送数</div>
              <div class="text-xl font-bold text-blue-600">{{ conditionSummary.condition_push_length }}</div>
            </div>
            <div
              class="bg-blue-50 border border-blue-200 rounded-lg p-3"
            >
              <div class="text-sm text-gray-600">子单委托推送数</div>
              <div class="text-xl font-bold text-blue-600">{{ conditionSummary.order_push_length }}</div>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-2 mb-2 mt-4">
          <p class="font-bold text-blue-900">按请求时间检索母单请求</p>
          <el-select v-model="currentTime" size="small" style="width: 200px;" placeholder="请选择请求时间">
            <el-option v-for="item in timeList" :key="item" :label="item" :value="item"></el-option>
          </el-select>
          <el-button @click="queryConditionOrderData" :loading="isLoadingConditionQueryData" size='small' type="primary">查询</el-button>
        </div>
        <common-table :data="currentTableData">
          <template #order_no="{ row }">
            <copy-text :text="row.order_no"></copy-text>
          </template>
        </common-table>
      </div>
      <div>
        <div class="flex items-center gap-2 mb-2 mt-4">
          <p class="font-bold text-blue-900">查询条件母单详情</p>
          <el-input v-model="conditionInstanceInstanceId" size="small" style="width: 200px;" placeholder="请输入母单实例ID" clearable></el-input>
          <el-button @click="queryConditionDetailData" :loading="isLoadingDetailData" size='small' type="primary">查询</el-button>
        </div>
        <div>
          <h4 class="font-bold my-2">母单创建详情</h4>
          <common-table :data="conditionInstanceDetailForRequestParams"></common-table>
        </div>
        <div>
          <h4 class="font-bold my-2">当日母单操作</h4>
          <common-table :data="conditionInstanceDetailForOperations"></common-table>
        </div>
        <h4 class="font-bold my-2">母单关联的股票列表({{ conditionInstanceDetailForStockList.length }}):</h4>
        <div>
          <span v-for="(item, index) in conditionInstanceDetailForStockList" :key="item">
            <copy-text :text="item"></copy-text>
            <span v-if="index !== conditionInstanceDetailForStockList.length - 1">、</span>
          </span>
        </div>
        <h4 class="font-bold my-2">监控条件列表({{ conditionInstanceDetailForConditionList.length }}):</h4>
        <div>
          <span v-for="(item, index) in conditionInstanceDetailForConditionList" :key="item">
            <copy-text :text="item"></copy-text>
            <span v-if="index !== conditionInstanceDetailForConditionList.length - 1">、</span>
          </span>
        </div>
        <div>
          <h4 class="font-bold my-2">母单股票委托列表</h4>
          <common-table :data="conditionInstanceDetailForGradeConditionDetail"></common-table>
        </div>
        <div>
          <h4 class="font-bold my-2">母单推送列表</h4>
          <common-table :data="conditionInstanceDetailForPushList"></common-table>
        </div>
        <div>
          <h4 class="font-bold my-2">母单修改信息列表</h4>
          <common-table :data="conditionInstanceDetailForModifyInformation"></common-table>
        </div>
        <div>
          <h4 class="font-bold my-2">母单首条推送信息列表</h4>
          <monaco-editor
            v-if="Object.keys(conditionInstanceDetailForFirstPush).length > 0"
            :modelValue="JSON.stringify(conditionInstanceDetailForFirstPush, null, 2)"
            language="json"
            :readonly="true"
            height="400px"
          />
        </div>
      </div>
      <div>
        <div class="flex items-center gap-2 mb-2 mt-4">
          <p class="font-bold text-blue-900">查询条件子单详情</p>
          <el-input v-model="conditionOrderInstanceId" size="small" style="width: 200px;" placeholder="请输入母单实例ID" clearable></el-input>
          <el-button @click="queryConditionOrderDetailData" :loading="isLoadingConditionOrderDetailData" size='small' type="primary">查询</el-button>
        </div>
        <h4 class="font-bold my-2">子单监控条件列表({{ conditionOrderDetailForConditionList.length }}):</h4>
        <div>
          <span v-for="(item, index) in conditionOrderDetailForConditionList" :key="item">
            <copy-text :text="item"></copy-text>
            <span v-if="index !== conditionOrderDetailForConditionList.length - 1">、</span>
          </span>
        </div>
        <div>
          <h4 class="font-bold my-2">子单状态列表</h4>
          <common-table :data="conditionOrderDetailForGradeConditionDetail"></common-table>
        </div>
      </div>
      <div>
        <div class="flex items-center gap-2 mb-2 mt-4">
          <p class="font-bold text-blue-900">查询条件子单详情</p>
          <el-input v-model="stockcode" size="small" style="width: 200px;" placeholder="筛选股票代码" clearable></el-input>
          <el-input v-model="conditionSecurityOrderInstanceId" size="small" style="width: 200px;" placeholder="请输入母单实例ID" clearable></el-input>
          <el-button @click="queryConditionSecurityOrderDetailData" :loading="isLoadingConditionSecurityOrderDetailData" size='small' type="primary">查询</el-button>
        </div>
        <div>
          <h4 class="font-bold my-2">子单个股下单参数</h4>
          <monaco-editor
            v-if="Object.keys(conditionSecurityOrderDetailForParams).length > 0"
            :modelValue="JSON.stringify(conditionSecurityOrderDetailForParams, null, 2)"
            language="json"
            :readonly="true"
            height="400px"
          />
        </div>
        <div>
          <h4 class="font-bold my-2">子单个股推送列表</h4>
          <common-table :data="conditionSecurityOrderDetailForPushList"></common-table>
        </div>
        <div>
          <h4 class="font-bold my-2">子单个股推送报错列表</h4>
          <common-table :data="conditionSecurityOrderDetailForErrorMsgs"></common-table>
        </div>
      </div>
    </template>
  </dataPanel>
</template>

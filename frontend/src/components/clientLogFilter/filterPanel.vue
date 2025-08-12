<script setup>
import { ref, computed } from 'vue';
import { useClientLogAnalyser } from '@/composable/clientLog';
import dataPanel from '@/components/common/dataPanel.vue';
import { Document } from '@element-plus/icons-vue';
import JsonViewerDialog from '@/components/common/JsonViewerDialog.vue';
import { parseClientLogLine } from '@/composable/clientLogParser';

const { filterLogList } = useClientLogAnalyser();

const isLoadingData = ref(false);
const content = ref('');
const filterLogListData = ref([]);

// 分页相关状态
const currentPage = ref(1);
const pageSize = ref(20);
const pageSizeOptions = [10, 20, 50, 100];

// 计算分页后的数据
const paginatedData = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value;
  const endIndex = startIndex + pageSize.value;
  return filterLogListData.value.slice(startIndex, endIndex);
});

// 计算总页数
const totalPages = computed(() => {
  return Math.ceil(filterLogListData.value.length / pageSize.value);
});

// 计算总数据量
const totalDataCount = computed(() => {
  return filterLogListData.value.length;
});

// 页码改变处理
const handlePageChange = (page) => {
  currentPage.value = page;
};

// 每页显示数量改变处理
const handleSizeChange = (size) => {
  pageSize.value = size;
  currentPage.value = 1; // 重置到第一页
};

const refreshData = async () => {
  isLoadingData.value = true;
  const data = await filterLogList({ content: content.value});
  filterLogListData.value = data.map(item => ({
    ...item,
    ...parseClientLogLine(item.content)
  }));
  // 重置分页到第一页
  currentPage.value = 1;
  isLoadingData.value = false;
};

// 清空数据
const clearData = () => {
  filterLogListData.value = [];
  content.value = '';
  // 重置分页
  currentPage.value = 1;
};

const jsonDialogVisible = ref(false);
const currentJson = ref('');
function showJson(json) {
  if (json) {
    currentJson.value = json;
    jsonDialogVisible.value = true;
  }
}
</script>

<template>
  <dataPanel title="日志筛选器">
    <template #actions>
        <el-input v-model="content" size="small" style="width: 200px;" placeholder="请输入内容" clearable></el-input>
        <el-button @click="refreshData" :loading="isLoadingData" size='small' type="primary">查询</el-button>
        <el-button @click="clearData" size='small' type="info" plain>清空</el-button>
    </template>
    <template #data>

      <!-- 空状态显示 -->
      <div v-if="filterLogListData.length === 0" class="flex flex-col items-center justify-center py-12 text-gray-500">
        <el-icon class="text-4xl mb-4 text-gray-300">
          <Document />
        </el-icon>
        <p class="text-lg">暂无数据</p>
        <p class="text-sm mt-2">请输入查询条件并点击查询按钮</p>
      </div>
      <!-- 数据列表 -->
      <div v-else class="space-y-4">
        <!-- 数据统计信息 -->
        <div class="flex items-center justify-between text-sm text-gray-600 mb-4">
          <span>共 {{ totalDataCount }} 条记录</span>
          <span>第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
        </div>
        
        <div v-for="(item, index) in paginatedData" :key="index"
             class="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow duration-200">
          <!-- 文本内容区域 -->
          <div class="p-4">
            <div class="flex items-start justify-between mb-3">
              <div class="flex items-center space-x-2">
                <el-icon class="text-blue-500">
                  <Document />
                </el-icon>
                <span class="text-sm font-medium text-gray-700">日志条目 #{{ (currentPage - 1) * pageSize + index + 1 }}</span>
                <el-tag v-if="item.isError" type="danger">错误</el-tag>
                <el-tag v-if="item.isTimeout" type="danger">超时</el-tag>
                <el-tag v-if="item.isSkip" type="info">跳过</el-tag>
                <el-tag v-if="item.req_type === 'request'" type="success">请求</el-tag>
                <el-tag v-if="item.req_type === 'response'" type="warning">响应</el-tag>
              </div>
              <div class="flex items-center space-x-2">
                <el-button
                  v-if="item.hasJson"
                  @click="showJson(item.jsonStr)"
                  size="small"
                  type="primary"
                  plain
                  class="text-xs"
                >
                  解析json
                </el-button>
              </div>
            </div>

            <!-- 文本内容 -->
            <div class="bg-gray-50 rounded-md p-3 border-l-4 border-blue-500">
              <p class="text-gray-800 leading-relaxed whitespace-pre-wrap break-words">
                {{ item.raw }}
              </p>
            </div>
          </div>
        </div>
        
        <!-- 分页组件 -->
        <div class="flex items-center justify-center mt-6">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="pageSizeOptions"
            :total="totalDataCount"
            :page-count="totalPages"
            layout="total, sizes, prev, pager, next, jumper"
            @current-change="handlePageChange"
            @size-change="handleSizeChange"
            background
            hide-on-single-page
          />
        </div>
      </div>
    </template>
  </dataPanel>
  <JsonViewerDialog v-model="jsonDialogVisible" :json="currentJson" />
</template>

<style scoped>
/* 自定义滚动条样式 */
.space-y-4 > div {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e0 #f7fafc;
}

.space-y-4 > div::-webkit-scrollbar {
  width: 6px;
}

.space-y-4 > div::-webkit-scrollbar-track {
  background: #f7fafc;
  border-radius: 3px;
}

.space-y-4 > div::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 3px;
}

.space-y-4 > div::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}
</style>

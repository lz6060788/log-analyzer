<template>
  <Teleport to="body">
    <el-dialog v-model="visible" title="日志详细信息" draggable width="60%" @close="onClose">
      <div v-if="logDetail" class="log-detail-content">
        <!-- 基本信息 -->
        <div class="basic-info mb-6">
          <h3 class="text-lg font-semibold mb-4 text-gray-800">基本信息</h3>
          <div class="grid grid-cols-2 gap-4">
            <div v-if="logDetail.time" class="info-item">
              <span class="label">时间:</span>
              <span class="value">{{ logDetail.time }}</span>
            </div>
            <div v-if="logDetail.id" class="info-item">
              <span class="label">ID:</span>
              <span class="value">{{ logDetail.id }}</span>
            </div>
            <div v-if="logDetail.recordType" class="info-item">
              <span class="label">记录类型:</span>
              <span class="value">{{ logDetail.recordType }}</span>
            </div>
            <div v-if="logDetail.protocol" class="info-item">
              <span class="label">协议:</span>
              <span class="value">{{ logDetail.protocol }}</span>
            </div>
            <div v-if="logDetail.serviceName" class="info-item">
              <span class="label">服务名称:</span>
              <span class="value">{{ logDetail.serviceName }}</span>
            </div>
            <div v-if="logDetail.action" class="info-item">
              <span class="label">操作:</span>
              <span class="value">{{ logDetail.action }}</span>
            </div>
            <div v-if="logDetail.pushType" class="info-item">
              <span class="label">推送类型:</span>
              <span class="value">{{ logDetail.pushType }}</span>
            </div>
          </div>
        </div>

        <!-- 详细内容 -->
        <div v-if="logDetail.content" class="content-section">
          <h3 class="text-lg font-semibold mb-4 text-gray-800">详细内容</h3>
          <div class="content-tabs">
            <el-tabs v-model="activeTab" type="border-card">
              <!-- JSON格式 -->
              <el-tab-pane label="JSON格式" name="json">
                <div class="json-content">
                  <MonacoEditor
                    v-model="jsonContent"
                    language="json"
                    :readonly="true"
                    height="400px"
                    theme="vs-dark"
                  />
                </div>
              </el-tab-pane>

              <!-- 原始格式 -->
              <el-tab-pane label="原始格式" name="raw">
                <div class="raw-content">
                  <MonacoEditor
                    v-model="rawContent"
                    language="client-log"
                    theme="client-log-theme"
                    :readonly="true"
                    height="400px"
                    :default-word-wrap="false"
                  />
                </div>
              </el-tab-pane>

              <!-- 格式化表格 -->
              <el-tab-pane label="表格格式" name="table" v-if="tableData.length > 0">
                <div class="table-content">
                  <el-table :data="tableData" border style="width: 100%">
                    <el-table-column prop="key" label="字段名" width="200" />
                    <el-table-column prop="value" label="字段值" />
                    <el-table-column prop="type" label="类型" width="100" />
                  </el-table>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="actions mt-6 flex justify-between items-center">
          <!-- 导航按钮 -->
          <div class="flex space-x-2">
            <el-button @click="handlePreviousLine" :disabled="!canGoPrevious" type="info">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
              </svg>
              上一条
            </el-button>
            <el-button @click="handleNextLine" :disabled="!canGoNext" type="info">
              下一条
              <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </el-button>
          </div>

          <!-- 右侧操作按钮 -->
          <div class="flex space-x-4">
            <el-button @click="copyContent" type="primary">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
              </svg>
              复制内容
            </el-button>
            <el-button @click="exportContent" type="success">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              导出
            </el-button>
          </div>
        </div>
      </div>
      <div v-else class="text-center text-gray-500 py-8">
        暂无日志详情信息
      </div>
    </el-dialog>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import MonacoEditor from './MonacoEditor.vue';
import { ElMessage } from 'element-plus';

const props = defineProps<{
  modelValue: boolean;
  logDetail?: any;
  currentLineNumber?: number; // 新增：当前行数
  totalLines?: number; // 新增：总行数
}>();

const emit = defineEmits(['update:modelValue', 'previous-line', 'next-line']);

const visible = ref(props.modelValue);
const activeTab = ref('json');

// 计算属性
const jsonContent = computed(() => {
  if (!props.logDetail?.content) return '';
  try {
    return JSON.stringify(JSON.parse(props.logDetail.content), null, 2);
  } catch {
    return props.logDetail.content;
  }
});

const rawContent = computed(() => {
  if (!props.logDetail?.content) return '';
  if (typeof props.logDetail.content === 'string') {
    return props.logDetail.content;
  }
  return JSON.stringify(props.logDetail.content, null, 2);
});

const tableData = computed(() => {
  if (!props.logDetail?.content || typeof props.logDetail.content !== 'object') {
    return [];
  }
  
  const data: Array<{ key: string; value: string; type: string }> = [];
  
  const flattenObject = (obj: any, prefix = '') => {
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        const value = obj[key];
        const fullKey = prefix ? `${prefix}.${key}` : key;
        
        if (value !== null && typeof value === 'object' && !Array.isArray(value)) {
          flattenObject(value, fullKey);
        } else {
          data.push({
            key: fullKey,
            value: Array.isArray(value) ? JSON.stringify(value) : String(value),
            type: Array.isArray(value) ? 'array' : typeof value
          });
        }
      }
    }
  };
  
  flattenObject(props.logDetail.content);
  return data;
});

// 计算属性：是否可以前往上一行
const canGoPrevious = computed(() => {
  return props.currentLineNumber && props.currentLineNumber > 1;
});

// 计算属性：是否可以前往下一行
const canGoNext = computed(() => {
  return props.currentLineNumber && props.totalLines && props.currentLineNumber < props.totalLines;
});

// 监听属性变化
watch(() => props.modelValue, (val) => {
  visible.value = val;
});

watch(() => props.logDetail, () => {
  if (props.logDetail?.content) {
    activeTab.value = 'json';
  }
});

// 方法
const onClose = () => {
  emit('update:modelValue', false);
};

const copyContent = async () => {
  try {
    const content = activeTab.value === 'json' ? jsonContent.value : 
                   activeTab.value === 'raw' ? rawContent.value : 
                   JSON.stringify(tableData.value, null, 2);
    
    await navigator.clipboard.writeText(content);
    ElMessage.success('内容已复制到剪贴板');
  } catch (error) {
    ElMessage.error('复制失败');
    console.error('Copy failed:', error);
  }
};

const exportContent = () => {
  try {
    const content = activeTab.value === 'json' ? jsonContent.value : 
                   activeTab.value === 'raw' ? rawContent.value : 
                   JSON.stringify(tableData.value, null, 2);
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `log_detail_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    ElMessage.success('内容已导出');
  } catch (error) {
    ElMessage.error('导出失败');
    console.error('Export failed:', error);
  }
};

// 处理上一行
const handlePreviousLine = () => {
  if (canGoPrevious.value) {
    emit('previous-line');
  }
};

// 处理下一行
const handleNextLine = () => {
  if (canGoNext.value) {
    emit('next-line');
  }
};
</script>

<style scoped>
.log-detail-content {
  max-height: 70vh;
  overflow-y: auto;
}

.info-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.info-item .label {
  font-weight: 600;
  color: #495057;
  margin-right: 8px;
  min-width: 80px;
}

.info-item .value {
  color: #212529;
  font-family: 'Consolas', 'Monaco', monospace;
  word-break: break-all;
}

.content-tabs {
  border: 1px solid #e9ecef;
  border-radius: 6px;
  overflow: hidden;
}

.json-content,
.raw-content {
  background-color: #1e1e1e;
  border-radius: 4px;
}

.table-content {
  max-height: 400px;
  overflow-y: auto;
}

.actions {
  border-top: 1px solid #e9ecef;
  padding-top: 16px;
}
</style> 
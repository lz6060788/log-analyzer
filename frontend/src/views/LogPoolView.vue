<template>
  <div class="min-h-[calc(100vh-32px)] bg-gray-50" :class="{ 'fixed inset-0 z-50': isFullscreen }">
    <!-- 顶部操作导航栏 -->
    <PageHeader>
      <template #actions>
        <button
          class="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          @click="refreshLogs"
          :disabled="isLoading"
        >
          <svg v-if="isLoading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isLoading ? '加载中...' : '刷新日志' }}
        </button>
        <button
          class="inline-flex items-center px-4 py-2 bg-gray-600 text-white text-sm font-medium rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          @click="exportLogs"
        >
          导出日志
        </button>
        <button
          class="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          @click="clearLogs"
        >
          清空日志
        </button>
        <button
          class="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          @click="toggleFullscreen"
        >
          <svg v-if="!isFullscreen" class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path>
          </svg>
          <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
          {{ isFullscreen ? '退出全屏' : '全屏' }}
        </button>
      </template>
    </PageHeader>

    <!-- 主要内容区域 -->
    <div class="flex h-[calc(100vh-80px)]" :class="{ 'h-screen': isFullscreen }">
      <!-- 左侧编辑器区域 -->
      <div class="w-[calc(100%-320px)] bg-white" :class="{ 'w-full': isFullscreen }">
        <MonacoEditor
          ref="monacoEditorRef"
          v-model="logContent"
          :height="editorHeight"
          :readonly="true"
          language="client-log"
          theme="client-log-theme"
          :show-minimap="true"
          :show-paste-dialog="true"
          :enable-interactive="true"
          @scroll="handleEditorScroll"
          @parse-log="handleParseLog"
          @log-click="handleLogClick"
        />
      </div>

      <!-- 右侧统计信息面板 -->
      <div v-if="!isFullscreen" class="w-80 bg-white border-l border-gray-200 p-4">
        <!-- 过滤模块 -->
        <div class="space-y-4 mb-6">
          <h3 class="text-lg font-medium text-gray-900">过滤设置</h3>
          <!-- 时间范围选择 -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">时间范围</label>
            <div class="flex space-x-2">
              <el-date-picker
                v-model="startTime"
                type="datetime"
                placeholder="开始时间"
                format="YYYYMMDD HH:mm:ss"
                value-format="YYYYMMDD HH:mm:ss"
                class="flex-1"
                size="default"
                clearable
              />
              <el-date-picker
                v-model="endTime"
                type="datetime"
                placeholder="结束时间"
                format="YYYYMMDD HH:mm:ss"
                value-format="YYYYMMDD HH:mm:ss"
                class="flex-1"
                size="default"
                clearable
              />
            </div>
            <div class="flex space-x-2">
              <button
                @click="clearTimeFilter"
                class="flex-1 px-3 py-1 text-xs text-gray-600 hover:text-gray-800 border border-gray-300 rounded hover:bg-gray-50"
              >
                清除时间
              </button>
              <button
                @click="setLastHour"
                class="flex-1 px-3 py-1 text-xs text-blue-600 hover:text-blue-800 border border-blue-300 rounded hover:bg-blue-50"
              >
                最近1小时
              </button>
            </div>
          </div>

          <!-- 条目数量限制 -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">显示条目</label>
            <select
              v-model="limitCount"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="1000">1000条</option>
              <option value="2000">2000条</option>
              <option value="5000">5000条</option>
              <option value="10000">10000条</option>
              <option value="-1">不限制</option>
            </select>
          </div>

          <!-- 过滤统计 -->
          <div class="p-3 bg-blue-50 rounded-lg">
            <div class="text-xs text-blue-700">
              <div class="flex justify-between">
                <span>原始条目:</span>
                <span class="font-medium">{{ originalLogCount }}</span>
              </div>
              <div class="flex justify-between">
                <span>过滤后:</span>
                <span class="font-medium">{{ filteredLogCount }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 统计信息 -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">统计信息</h3>
          <div class="space-y-3">
            <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <span class="text-sm text-gray-600">总行数:</span>
              <span class="text-sm font-medium text-gray-900">{{ totalLines }}</span>
            </div>
            <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <span class="text-sm text-gray-600">当前区间:</span>
              <span class="text-sm font-medium text-gray-900">{{ currentRange }}</span>
            </div>
            <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <span class="text-sm text-gray-600">可见行数:</span>
              <span class="text-sm font-medium text-gray-900">{{ visibleLines }}</span>
            </div>
          </div>
        </div>

        <!-- 功能说明 -->
        <div class="mt-6 p-4 bg-blue-50 rounded-lg">
          <h4 class="text-sm font-medium text-blue-900 mb-2">使用说明</h4>
          <ul class="text-xs text-blue-700 space-y-1">
            <li>• 可在minimap上拖拽快速定位</li>
            <li>• 双击有详细内容的日志行可查看详细信息</li>
            <li>• 右键菜单包含"解析选中日志"选项</li>
            <li>• 右键菜单包含"切换横向滚动条"选项</li>
            <li>• 日志关键字高亮自定义</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 日志详情对话框 -->
    <LogDetailDialog
      v-model="logDetailDialogVisible"
      :log-detail="currentLogDetail"
      :current-line-number="currentClickedLineNumber"
      :total-lines="displayLogList.length"
      @previous-line="handlePreviousLine"
      @next-line="handleNextLine"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, onUnmounted } from 'vue'
import MonacoEditor from '@/components/common/MonacoEditor.vue'
import LogDetailDialog from '@/components/common/LogDetailDialog.vue'
import { useClientLogAnalyser } from '@/composable/clientLog';
import { useOperationLogAnalyser } from '@/composable/operationLog';
import { parseTimeToTimestamp, mergeSortedArrays } from '@/utils/timeUtils';
import { openLogPasteDialog } from '@/components/common/logPasteDialog';
import PageHeader from '@/components/common/PageHeader.vue';

const { filterLogList: filterClientLogList } = useClientLogAnalyser();
const { filterLogList: filterOperationLogList } = useOperationLogAnalyser();

// 响应式数据
const logContent = computed(() => {
  return displayLogList.value.map(formatLogContent).join('\n')
})
const formatLogContent = (log: any) => {
  if (log.type === 'client') {
    if (log.record_type) {
      return `[${log.time}] 【${log.record_type}】 ${log.id} - 【${log.protocol}】|【${log.servicename}】|【${log.action}】`
    }
    if (log.push_type) {
      return `[${log.time}] 【${log.push_type}】 ${log.push_type === 'response_push' ? log.content : ''}`
    }
  }
  return `[${log.time}] ${log.content}`
}

const isLoading = ref<boolean>(false)
const editorHeight = ref<string>('100%')
const isFullscreen = ref<boolean>(false)
const monacoEditorRef = ref<InstanceType<typeof MonacoEditor> | null>(null)

// 日志详情对话框
const logDetailDialogVisible = ref<boolean>(false)
const currentLogDetail = ref<any>(null)
const currentClickedLineNumber = ref<number>(-1) // 新增：记住当前点击的行数

// 过滤相关数据
const startTime = ref<string>('')
const endTime = ref<string>('')
const limitCount = ref<string>('2000')

// 滚动相关数据
const currentScrollTop = ref<number>(0)
const currentScrollHeight = ref<number>(0)
const viewportHeight = ref<number>(0)

// 计算属性
const totalLines = computed(() => {
  if (!logContent.value) return 0
  return logContent.value.split('\n').length
})

const LINE_HEIGHT = 19
const currentRange = computed(() => {
  if (!currentScrollHeight.value || !viewportHeight.value) return '0-0'

  // 计算当前可见区域的起始行
  const startLine = Math.floor(currentScrollTop.value / LINE_HEIGHT) + 1

  // 计算固定跨度：当前可见的行数
  const visibleLineCount = Math.floor(viewportHeight.value / LINE_HEIGHT)
  const endLine = Math.min(startLine + visibleLineCount - 1, totalLines.value)

  return `${startLine}-${endLine}`
})

const visibleLines = computed(() => {
  if (!currentScrollHeight.value || !viewportHeight.value) return 0

  // 计算当前可见的行数（固定值）
  const visibleLineCount = Math.floor(viewportHeight.value / LINE_HEIGHT)
  return Math.min(visibleLineCount, totalLines.value)
})

// 查询
const clientLogList = ref<any[]>([])
const operationLogList = ref<any[]>([])
const fetchLogContent = async (): Promise<void> => {
  clientLogList.value = await filterClientLogList({ startTime: startTime.value, endTime: endTime.value }) || []
  operationLogList.value = await filterOperationLogList({ startTime: startTime.value, endTime: endTime.value }) || []
}

const totalLogList = computed(() => {
  // 使用双指针方法合并两个有序数组，性能更优
  return mergeSortedArrays(
    clientLogList.value,
    operationLogList.value,
    (a, b) => {
      const timeA = parseTimeToTimestamp(a.time, a.type)
      const timeB = parseTimeToTimestamp(b.time, b.type)
      return timeA - timeB
    }
  )
})
const displayLogList = computed(() => {
  // 应用数量限制
  const limit = parseInt(limitCount.value)
  if (limit > 0) {
    return totalLogList.value.slice(-limit) // 取最新的limit条记录
  }

  return totalLogList.value
})

// 原始日志数量（未过滤）
const originalLogCount = computed(() => {
  return totalLogList.value.length
})

// 过滤后的日志数量
const filteredLogCount = computed(() => {
  return displayLogList.value.length
})

const refreshLogs = async () => {
  isLoading.value = true
  try {
    await fetchLogContent()
  } catch (error) {
    console.error('刷新日志失败:', error)
  } finally {
    isLoading.value = false
  }
}

const exportLogs = () => {
  if (!totalLogList.value.length) {
    alert('没有日志内容可导出')
    return
  }

  const blob = new Blob([logContent.value], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `logs_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const clearLogs = () => {
  if (confirm('确定要清空所有日志内容吗？')) {
    clientLogList.value = []
    operationLogList.value = []
  }
}

// 时间过滤辅助函数
const clearTimeFilter = () => {
  startTime.value = ''
  endTime.value = ''
}

const setLastHour = () => {
  const now = new Date()
  const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000)

  // 格式化为Element Plus日期时间选择器需要的格式 (YYYY-MM-DD HH:mm:ss)
  const formatDate = (date: Date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  }

  startTime.value = formatDate(oneHourAgo)
  endTime.value = formatDate(now)
}

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value

  // 处理body滚动
  if (isFullscreen.value) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
}

const handleEditorScroll = (event: any) => {
  if (event && event.target) {
    currentScrollTop.value = event.target.scrollTop
    currentScrollHeight.value = event.target.scrollHeight
    viewportHeight.value = event.target.clientHeight
  }
}

// 处理日志解析
const handleParseLog = (selectedText: string) => {
  if (selectedText.trim()) {
    openLogPasteDialog(selectedText)
  }
}

// 解析日志行，提取详细信息
const parseLogLine = (lineNumber: number) => {
  if (!displayLogList.value || lineNumber < 1 || lineNumber > displayLogList.value.length) {
    return null;
  }

  const logData = displayLogList.value[lineNumber - 1];
  const details: any = {};

  // 提取基本信息
  if (logData.type === 'client') {
    details.type = '客户端日志';
    details.time = logData.time;
    details.id = logData.id;

    if (logData.record_type) {
      details.recordType = logData.record_type;
      details.protocol = logData.protocol;
      details.serviceName = logData.servicename;
      details.action = logData.action;
      details.content = logData.content; // 原始内容
    }

    if (logData.push_type) {
      details.pushType = logData.push_type;
      details.content = logData.content;
    }
  } else {
    details.type = '操作日志';
    details.time = logData.time;
    details.content = logData.content;
  }

  return details;
};

// 处理日志点击事件
const handleLogClick = (event: any) => {
  if (event.type === 'double-click') {
    // 记住当前点击的行数
    currentClickedLineNumber.value = event.lineNumber;

    // 解析日志行
    const details = parseLogLine(event.lineNumber);
    if (details) {
      currentLogDetail.value = details;
      logDetailDialogVisible.value = true;
    }
  }
};

// 处理上一行
const handlePreviousLine = () => {
  if (currentClickedLineNumber.value > 1) {
    currentClickedLineNumber.value--;
    const details = parseLogLine(currentClickedLineNumber.value);
    if (details) {
      currentLogDetail.value = details;
    }
  }
};

// 处理下一行
const handleNextLine = () => {
  if (currentClickedLineNumber.value < displayLogList.value.length) {
    currentClickedLineNumber.value++;
    const details = parseLogLine(currentClickedLineNumber.value);
    if (details) {
      currentLogDetail.value = details;
    }
  }
};

// 监听ESC键退出全屏
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && isFullscreen.value) {
    toggleFullscreen()
  }
}

// 生命周期
onMounted(async () => {
  await nextTick()
  // await refreshLogs()

  // 添加键盘事件监听
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  // 清理事件监听和样式
  document.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})
</script>

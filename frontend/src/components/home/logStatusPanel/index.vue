<script setup lang="ts">
import { CheckCircleIcon, ArrowPathIcon, XCircleIcon } from '@heroicons/vue/24/solid';
import { useClientLogAnalyser } from '@/composable/clientLog';
import { useOperationLogAnalyser } from '@/composable/operationLog';
import { LogAnalyserType, LogAnalyserStatusType } from '@/types';
import { ref, computed } from 'vue';
import { globalApi } from '@/api';
import { useGlobalStore } from '@/store/global';

// 获取客户端日志分析器
const clientLogAnalyser = useClientLogAnalyser();
// 获取操作日志分析器
const operationLogAnalyser = useOperationLogAnalyser();

const store = useGlobalStore();
globalApi.getStatus().then(res => {
  if (res.code === 0) {
    store.setLogAnalyserStatus(LogAnalyserType.Client, res.data.client_status ? LogAnalyserStatusType.Ready : LogAnalyserStatusType.None);
    store.setLogAnalyserStatus(LogAnalyserType.Operation, res.data.operation_status ? LogAnalyserStatusType.Ready : LogAnalyserStatusType.None);
  }
})

// 日志类型配置
const logTypes = [
  {
    type: LogAnalyserType.Client,
    title: '全量日志（支持多文件）',
    status: computed(() => clientLogAnalyser.clientLogAnalyserStatus.value),
    initFunction: clientLogAnalyser.initClientLogAnalyser,
    accept: '.log'
  },
  {
    type: LogAnalyserType.Operation,
    title: '操作日志（支持多文件）',
    status: computed(() => operationLogAnalyser.operationLogAnalyserStatus.value),
    initFunction: operationLogAnalyser.initOperationLogAnalyser,
    accept: '.log'
  }
];

// 根据状态获取样式类
const getStatusClasses = (status: LogAnalyserStatusType) => {
  const baseClasses = 'w-full h-10 p-2 flex items-center justify-between';
  const statusClasses = {
    [LogAnalyserStatusType.None]: 'bg-gray-100 cursor-pointer hover:bg-gray-200',
    [LogAnalyserStatusType.Ready]: 'bg-green-100 cursor-pointer hover:bg-green-200',
    [LogAnalyserStatusType.Running]: 'bg-orange-100',
    [LogAnalyserStatusType.Error]: 'bg-red-100 cursor-pointer hover:bg-red-200',
  };
  return `${baseClasses} ${statusClasses[status] || statusClasses[LogAnalyserStatusType.None]}`;
};

// 根据状态获取图标颜色类
const getIconClasses = (status: LogAnalyserStatusType) => {
  const iconClasses = {
    [LogAnalyserStatusType.None]: 'text-gray-400',
    [LogAnalyserStatusType.Ready]: 'text-green-400',
    [LogAnalyserStatusType.Running]: 'text-yellow-400',
    [LogAnalyserStatusType.Error]: 'text-red-400',
  };
  return iconClasses[status] || iconClasses[LogAnalyserStatusType.None];
};

// 根据状态获取状态文本
const getStatusText = (status: LogAnalyserStatusType) => {
  const statusTexts = {
    [LogAnalyserStatusType.None]: '未就绪',
    [LogAnalyserStatusType.Ready]: '已就绪',
    [LogAnalyserStatusType.Running]: '解析中',
    [LogAnalyserStatusType.Error]: '解析错误',
  };
  return statusTexts[status] || statusTexts[LogAnalyserStatusType.None];
};

// 根据状态获取图标
const getStatusIcon = (status: LogAnalyserStatusType) => {
  if (status === LogAnalyserStatusType.Running) {
    return ArrowPathIcon;
  } else if (status === LogAnalyserStatusType.Error) {
    return XCircleIcon;
  } else {
    return CheckCircleIcon;
  }
};

// 开始日志分析器
const startLogAnalyser = (logType: LogAnalyserType) => {
  const logConfig = logTypes.find(config => config.type === logType);
  if (!logConfig || logConfig.status.value === LogAnalyserStatusType.Running) {
    return;
  }
  const logInputRef = `${logType}logInput`;
  document.getElementById(logInputRef)?.click();
};

// 处理日志文件变化
const handleLogChange = async (e: Event, logType: LogAnalyserType) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    const files = Array.from(target.files);
    const logConfig = logTypes.find(config => config.type === logType);
    if (logConfig) {
      await logConfig.initFunction(files);
    }
  }
  target.value = '';
};
</script>

<template>
  <div
    class="flex gap-4 p-2 bg-blue-100 rounded-lg"
  >
    <template v-for="logConfig in logTypes" :key="logConfig.type">
      <div
        :class="getStatusClasses(logConfig.status.value)"
        @click="startLogAnalyser(logConfig.type)"
      >
        <span class="text-gray-600">{{ logConfig.title }}</span>
        <div
          class="flex items-center gap-4"
          :class="getIconClasses(logConfig.status.value)"
        >
          <span>{{ getStatusText(logConfig.status.value) }}</span>
          <component
            :is="getStatusIcon(logConfig.status.value)"
            class="size-6"
            :class="{ 'animate-spin': logConfig.status.value === LogAnalyserStatusType.Running }"
          />
        </div>
        <input
          type="file"
          :name="`${logConfig.type}log`"
          :id="`${logConfig.type}logInput`"
          class="hidden"
          multiple
          :accept="logConfig.accept"
          @change="(e) => handleLogChange(e, logConfig.type)"
        >
      </div>
    </template>
  </div>
</template>

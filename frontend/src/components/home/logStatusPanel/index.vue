<script setup lang="ts">
import { CheckCircleIcon, ArrowPathIcon, XCircleIcon } from '@heroicons/vue/24/solid';
import { useClientLogAnalyser } from '@/composable/clientLog';
import { LogAnalyserType, LogAnalyserStatusType } from '@/types';
import { ref } from 'vue';

const {
  clientLogAnalyserStatus,
  initClientLogAnalyser,
} = useClientLogAnalyser();

const clientLogInputRef = ref();
const startClientLogAnalyser =  () => {
  if (clientLogAnalyserStatus.value === LogAnalyserStatusType.Running) {
    return;
  }
  clientLogInputRef.value?.click();
}
const handleClientLogChange = async (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files) {
    await initClientLogAnalyser(target.files[0])
  }
  target.value = ''
}
</script>

<template>
  <div class="p-2 bg-blue-100 w-80 rounded-lg">
    <div
      class="w-full h-10 p-2 flex items-center justify-between"
      :class="{
        'bg-gray-100 cursor-pointer hover:bg-gray-200': clientLogAnalyserStatus === LogAnalyserStatusType.None,
        'bg-green-100 cursor-pointer hover:bg-green-200': clientLogAnalyserStatus === LogAnalyserStatusType.Ready,
        'bg-orange-100': clientLogAnalyserStatus === LogAnalyserStatusType.Running,
        'bg-red-100 cursor-pointer hover:bg-red-200': clientLogAnalyserStatus === LogAnalyserStatusType.Error,
      }"
      @click="startClientLogAnalyser"
    >
      <span class="text-gray-600">全量日志</span>
      <div
        class="flex items-center gap-4"
        :class="{
          'text-gray-400': clientLogAnalyserStatus === LogAnalyserStatusType.None,
          'text-green-400': clientLogAnalyserStatus === LogAnalyserStatusType.Ready,
          'text-yellow-400': clientLogAnalyserStatus === LogAnalyserStatusType.Running,
          'text-red-400': clientLogAnalyserStatus === LogAnalyserStatusType.Error,
        }"
      >
        <template v-if="clientLogAnalyserStatus === LogAnalyserStatusType.None">
          <span>未就绪</span>
          <CheckCircleIcon class="size-6" />
        </template>
        <template v-else-if="clientLogAnalyserStatus === LogAnalyserStatusType.Running">
          <span>解析中</span>
          <ArrowPathIcon class="size-6 animate-spin" />
        </template>
        <template v-else-if="clientLogAnalyserStatus === LogAnalyserStatusType.Ready">
          <span>已就绪</span>
          <CheckCircleIcon class="size-6" />
        </template>
        <template v-else-if="clientLogAnalyserStatus === LogAnalyserStatusType.Error">
          <span>解析错误</span>
          <XCircleIcon class="size-6" />
        </template>
      </div>
      <input ref="clientLogInputRef" type="file" name="clientlog" id="clientlog" class="hidden" @change="handleClientLogChange">
    </div>
  </div>
</template>

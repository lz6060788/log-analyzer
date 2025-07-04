<script setup>
import { computed } from 'vue';
import { CheckCircleIcon, ArrowPathIcon } from '@heroicons/vue/24/solid'
</script>

<template>
  <div class="p-2 bg-blue-100 w-80 rounded-lg">
    <div class="w-full h-10 p-2 flex items-center justify-between bg-gray-100 cursor-pointer">
      <span class="text-gray-600">全量日志</span>
      <div class="flex items-center gap-4 text-gray-400">
        <span>未就绪</span>
        <CheckCircleIcon class="size-6" />
      </div>
    </div>
    <div class="w-full h-10 p-2 flex items-center justify-between bg-orange-100">
      <span class="text-gray-600">全量日志</span>
      <div class="flex items-center gap-4 text-orange-400">
        <span>解析中</span>
        <ArrowPathIcon class="size-6 animate-spin" />
      </div>
    </div>
    <div class="w-full h-10 p-2 flex items-center justify-between bg-green-100 cursor-pointer">
      <span class="text-gray-600">全量日志</span>
      <div class="flex items-center gap-4 text-green-400">
        <span>已就绪</span>
        <CheckCircleIcon class="size-6" />
      </div>
    </div>
  </div>
</template>

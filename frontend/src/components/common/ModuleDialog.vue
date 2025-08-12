<template>
  <div
    v-if="isVisible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    @click="closeDialog"
  >
    <div
      class="flex flex-col w-full max-w-4xl mx-4 bg-white rounded-lg shadow-2xl border border-gray-200 max-h-[90vh] overflow-hidden"
      @click.stop
    >
      <!-- 弹窗头部 -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
        <div class="flex items-center space-x-3">
          <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
            <p v-if="description" class="text-sm text-gray-500">{{ description }}</p>
          </div>
        </div>

        <!-- 关闭按钮 -->
        <button
          @click="closeDialog"
          class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors duration-150"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 弹窗内容 -->
      <div class="flex-1 overflow-y-auto p-6">
        <component
          :is="moduleComponent"
          v-if="moduleComponent"
          v-bind="moduleProps"
          @close="closeDialog"
        />
      </div>

      <!-- 弹窗底部 -->
      <div class="flex items-center justify-between p-4 border-t border-gray-200 bg-gray-50">
        <div class="text-sm text-gray-500">
          按 <kbd class="px-2 py-1 text-xs font-semibold text-gray-500 bg-gray-100 border border-gray-200 rounded">ESC</kbd> 关闭
        </div>
        <button
          @click="closeDialog"
          class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 transition-colors duration-150"
        >
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, nextTick, watch } from 'vue'
import type { Component } from 'vue'

// Props
interface Props {
  /** 弹窗标题 */
  title: string
  /** 弹窗描述 */
  description?: string
  /** 要显示的模块组件 */
  moduleComponent: Component
  /** 传递给模块组件的属性 */
  moduleProps?: Record<string, any>
}

const props = withDefaults(defineProps<Props>(), {
  moduleProps: () => ({})
})

// Emits
const emit = defineEmits<{
  close: []
}>()

// 响应式数据
const isVisible = ref(false)

// 计算属性
const dialogTitle = computed(() => props.title)
const dialogDescription = computed(() => props.description)

// 方法
const openDialog = () => {
  isVisible.value = true
  
  // 绑定 ESC 键关闭弹窗
  nextTick(() => {
    document.addEventListener('keydown', handleKeydown)
  })
}

const closeDialog = () => {
  isVisible.value = false
  document.removeEventListener('keydown', handleKeydown)
  emit('close')
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    closeDialog()
  }
}

// 监听弹窗状态变化，清理事件监听器
watch(isVisible, (newValue) => {
  if (!newValue) {
    document.removeEventListener('keydown', handleKeydown)
  }
})

// 暴露方法给父组件
defineExpose({
  openDialog,
  closeDialog
})
</script>

<style scoped>
/* 自定义滚动条样式 */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>

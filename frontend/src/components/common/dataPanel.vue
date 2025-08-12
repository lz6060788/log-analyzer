<template>
  <div
    class="bg-blue-50 bg-opacity-80 backdrop-blur-md rounded-2xl overflow-hidden shadow-sm transition-all duration-300 pb-4 mb-8 last:mb-0"
    :class="fullScreenCls"
  >
    <!-- 卡片标题与操作区域 -->
    <div class="flex justify-between items-center bg-orange-100 px-4 py-2 border-0 border-b-2 border-gray-200 border-solid">
      <!-- 卡片标题 -->
      <h3 class="text-lg font-semibold select-none" :id="title">{{ title }}</h3>

      <!-- 操作按钮区域 -->
      <div class="flex items-center gap-2">
        <!-- 全屏切换按钮 -->
        <ArrowsPointingOutIcon
          v-if="!isFullscreen"
          class="h-5 w-5 hover:text-blue-500 cursor-pointer"
          @click="toggleFullscreen"
        ></ArrowsPointingOutIcon>
        <ArrowsPointingInIcon
          v-else
          class="h-5 w-5 hover:text-blue-500 cursor-pointer"
          @click="toggleFullscreen"
        ></ArrowsPointingInIcon>

        <!-- 展开/收起按钮 -->
        <ChevronDoubleUpIcon
          class="h-5 w-5 hover:text-blue-500 cursor-pointer"
          :class="expanded ? 'rotate-0' : 'rotate-180'"
          @click="toggleExpand"
        ></ChevronDoubleUpIcon>
      </div>
    </div>

    <div v-show="expanded" class="w-full mt-4">
      <!-- 操作区域 -->
      <div class="w-full flex items-center gap-2 px-4">
        <slot name="actions">
          <!-- 默认操作内容 -->
        </slot>
      </div>

      <div v-if="expanded" class="p-4">
        <slot name="data">
          <!-- 默认数据内容 -->
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { ChevronDoubleUpIcon, ArrowsPointingInIcon, ArrowsPointingOutIcon } from '@heroicons/vue/24/solid'

const props = defineProps({
  title: {
    type: String,
    required: true
  }
});

const expanded = ref(true);
const isFullscreen = ref(false);

const toggleExpand = () => {
  expanded.value = !expanded.value;
};

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value;
};
const fullScreenCls = computed(() => {
  return isFullscreen.value ? 'fixed left-0 top-0 w-screen h-screen' : ''
})
</script>

<style scoped>
/* 组件样式 */
.slide-enter-active, .slide-leave-active {
  transition: all 0.3s ease-in-out;
}
.slide-enter-from, .slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>

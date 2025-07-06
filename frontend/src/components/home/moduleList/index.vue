<template>
  <div
    class="w-full min-w-[800px] mx-auto flex flex-wrap gap-5 p-5 border border-gray-200 bg-gray-300 rounded mt-6"
>
    <div
        v-for="(item, index) in modules"
        :key="index"
        class="flex-1 min-w-[calc(20%-20px)] max-w-[calc(33.333%-20px)] h-36 rounded-lg bg-white shadow-sm hover:translate-y-[-5px] hover:shadow-lg transition-all cursor-pointer items-center justify-center bg-blue-50"
    >
      <div class="card-content text-center p-4">
        <h3>{{ item.title }}</h3>
        <p>{{ item.description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface ModuleItem {
  title: string;
  description: string;
}

const modules = ref<ModuleItem[]>([
  {
    title: '全量日志检索',
    description: '解析全量日志中的各请求数据，以表格形式展示数据内容，支持多项过滤功能，目前已适配主要接口',
  },
  {
    title: '功能 2',
    description: '这是第二个功能的描述',
  },
  {
    title: '功能 3',
    description: '这是第三个功能的描述',
  },
  {
    title: '功能 4',
    description: '这是第四个功能的描述',
  },
  {
    title: '功能 5',
    description: '这是第五个功能的描述',
  },
]);

const hoverModule = (index: number) => {
  // 鼠标悬停逻辑
};

const leaveModule = (index: number) => {
  // 鼠标离开逻辑
};

const clickModule = (item: ModuleItem) => {
  // 点击逻辑
};
</script>

<style scoped>
/* 移除原有的 CSS 样式，使用 Tailwind CSS 类名 */
</style>
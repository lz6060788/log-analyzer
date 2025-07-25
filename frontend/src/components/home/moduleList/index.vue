<template>
  <div class="w-full min-w-[800px] mx-auto grid grid-cols-12 gap-4 mt-6">
    <div
      v-for="(item, index) in modules"
      :key="index"
      class="group relative overflow-hidden rounded-3xl bg-gradient-to-br from-white/70 to-gray-100/70 backdrop-blur-xl shadow-lg hover:shadow-2xl transform transition-all duration-300 cursor-pointer mb-6 pb-2"
      :class="[
        item.size === 'large' ? 'col-span-6' : 'col-span-3',
        item.color === 'blue-purple' ? 'from-blue-500/20 to-purple-600/20' : '',
        item.color === 'green-teal' ? 'from-green-500/20 to-teal-600/20' : '',
        item.color === 'amber-pink' ? 'from-amber-500/20 to-pink-600/20' : '',
        item.color === 'sky-blue' ? 'from-sky-400/20 to-blue-500/20' : '',
        item.color === 'orange' ? 'from-orange-400/20 to-amber-500/20' : ''
      ]"
      @click="jumpToPath(item)"
    >
      <div 
        class="absolute inset-0 opacity-80"
        :class="{
          'bg-gradient-to-br from-blue-100 via-transparent to-purple-100': item.color === 'blue-purple',
          'bg-gradient-to-br from-green-100 via-transparent to-teal-100': item.color === 'green-teal',
          'bg-gradient-to-br from-amber-100 via-transparent to-pink-100': item.color === 'amber-pink',
          'bg-gradient-to-br from-sky-100 via-transparent to-blue-100': item.color === 'sky-blue',
          'bg-gradient-to-br from-orange-100 via-transparent to-amber-100': item.color === 'orange'
        }"
      ></div>
      <div class="relative z-10 flex flex-col items-center justify-center p-5 text-center">
        <h3 class="text-lg font-semibold text-gray-800 group-hover:text-blue-600 transition-colors">{{ item.title }}</h3>
        <p class="h-10 text-sm text-gray-600 mt-2 overflow-hidden text-ellipsis line-clamp-2">{{ item.description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';

interface ModuleItem {
  title: string;
  description: string;
  size?: string;
  color?: 'blue-purple' | 'green-teal' | 'amber-pink' | 'sky-blue' | 'orange';
  path?: string;
}

const modules = ref<ModuleItem[]>([
  {
    title: '全量日志检索',
    description: '解析全量日志中的各请求数据，以表格形式展示数据内容，支持多项过滤功能，目前已适配主要接口',
    size: 'large',
    color: 'blue-purple',
    path: '/clientLogFilter',
  },
  {
    title: '日志解析美化工具',
    description: '简单解析日志内容，格式化显示json内容，表格形式展示日志片段内容',
    color: 'green-teal',
    path: '/log-paste',
  },
  {
    title: '功能 3',
    description: '这是第三个功能的描述',
    color: 'amber-pink'
  },
  {
    title: '功能 4',
    description: '这是第四个功能的描述',
    color: 'sky-blue'
  },
  {
    title: '功能 5',
    description: '这是第五个功能的描述',
    color: 'orange'
  },
]);

const router = useRouter();
const jumpToPath = (item: ModuleItem) => {
  if (item.path) {
    router.push(item.path);
  }
};
</script>

<template>
  <!-- 搜索遮罩层 -->
  <div
    v-if="isVisible"
    class="fixed inset-0 z-50 flex items-start justify-center pt-20 bg-black/50 backdrop-blur-sm"
    @click="closeSearch"
  >
    <!-- 搜索框容器 -->
    <div
      class="w-full max-w-2xl mx-4 bg-white rounded-lg shadow-2xl border border-gray-200"
      @click.stop
    >
      <!-- 搜索输入框 -->
      <div class="p-4 border-b border-gray-100">
        <div class="relative">
          <input
            ref="searchInput"
            v-model="searchQuery"
            type="text"
            :placeholder="config.placeholder || '搜索功能、页面、操作...'"
            class="w-full pl-10 pr-4 py-3 text-lg border-0 outline-none placeholder-gray-400 focus:ring-0"
            @input="handleSearch"
            @keydown="handleKeydown"
          />
          <div class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <!-- 快捷键提示 -->
          <div class="absolute right-3 top-1/2 transform -translate-y-1/2">
            <kbd class="px-2 py-1 text-xs font-semibold text-gray-500 bg-gray-100 border border-gray-200 rounded">ESC</kbd>
          </div>
        </div>
      </div>

      <!-- 搜索结果列表 -->
      <div v-if="searchQuery && filteredResults.length > 0" class="max-h-96 overflow-y-auto">
        <div
          v-for="(result, index) in filteredResults"
          :key="result.item.id"
          :class="[
            'px-4 py-3 cursor-pointer hover:bg-gray-50 transition-colors duration-150',
            selectedIndex === index ? 'bg-blue-50 border-l-4 border-blue-500' : ''
          ]"
          @click="selectResult(result)"
          @mouseenter="selectedIndex = index"
        >
          <div class="flex items-center space-x-3">
            <!-- 图标 -->
            <div v-if="result.item.icon" class="flex-shrink-0 w-8 h-8 text-gray-400">
              <svg class="w-full h-full" fill="currentColor" viewBox="0 0 24 24">
                <path :d="result.item.icon" />
              </svg>
            </div>
            <div v-else class="flex-shrink-0 w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
            
            <!-- 内容 -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center space-x-2">
                <span class="text-sm font-medium text-gray-900">{{ result.item.title }}</span>
                <span v-if="result.item.category" class="px-2 py-1 text-xs text-gray-500 bg-gray-100 rounded-full">
                  {{ result.item.category }}
                </span>
              </div>
              <p v-if="result.item.description" class="text-sm text-gray-500 mt-1 truncate">
                {{ result.item.description }}
              </p>
            </div>

            <!-- 匹配关键词高亮 -->
            <div v-if="result.matchedKeywords.length > 0" class="flex-shrink-0 text-xs text-gray-400">
              <span v-for="keyword in result.matchedKeywords.slice(0, 2)" :key="keyword" class="px-1 py-0.5 bg-yellow-100 text-yellow-800 rounded mr-1">
                {{ keyword }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 无搜索结果提示 -->
      <div v-else-if="searchQuery && !isSearching" class="px-4 py-8 text-center text-gray-500">
        <svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-3.169 0-6-2.791-6-6s2.831-6 6-6c3.169 0 6 2.791 6 6 0 1.528-.538 2.931-1.428 4.291" />
        </svg>
        <p class="text-sm">未找到相关结果</p>
        <p class="text-xs text-gray-400 mt-1">尝试使用其他关键词</p>
      </div>

      <!-- 搜索中状态 -->
      <div v-else-if="isSearching" class="px-4 py-8 text-center text-gray-500">
        <div class="animate-spin w-8 h-8 mx-auto border-2 border-gray-300 border-t-blue-500 rounded-full mb-3"></div>
        <p class="text-sm">搜索中...</p>
      </div>

      <!-- 默认提示 -->
      <div v-else class="px-4 py-8 text-center text-gray-500">
        <svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <p class="text-sm">开始输入关键词进行搜索</p>
        <p class="text-xs text-gray-400 mt-1">支持功能、页面、操作等搜索</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, nextTick, watch } from 'vue'
import type { SearchItem, SearchConfig, SearchResult } from '@/types/search'

// Props
interface Props {
  /** 搜索项列表 */
  items: SearchItem[]
  /** 搜索配置 */
  config?: SearchConfig
}

const props = withDefaults(defineProps<Props>(), {
  config: () => ({
    placeholder: '搜索功能、页面、操作...',
    showCategories: true,
    maxResults: 10
  })
})

// Emits
const emit = defineEmits<{
  close: []
  select: [item: SearchItem]
}>()

// 响应式数据
const isVisible = ref(false)
const searchQuery = ref('')
const selectedIndex = ref(0)
const isSearching = ref(false)
const searchInput = ref<HTMLInputElement>()

// 计算属性
const filteredResults = computed(() => {
  if (!searchQuery.value.trim()) return []
  
  const query = searchQuery.value.toLowerCase()
  const results: SearchResult[] = []
  
  for (const item of props.items) {
    const score = calculateScore(item, query)
    if (score > 0) {
      results.push({
        item,
        score,
        matchedKeywords: getMatchedKeywords(item, query)
      })
    }
  }
  
  // 按分数排序并限制结果数量
  return results
    .sort((a, b) => b.score - a.score)
    .slice(0, props.config.maxResults)
})

// 方法
const calculateScore = (item: SearchItem, query: string): number => {
  let score = 0
  
  // 标题匹配
  if (item.title.toLowerCase().includes(query)) {
    score += 100
  }
  
  // 描述匹配
  if (item.description && item.description.toLowerCase().includes(query)) {
    score += 50
  }
  
  // 关键词匹配
  if (item.keywords) {
    for (const keyword of item.keywords) {
      if (keyword.toLowerCase().includes(query)) {
        score += 75
      }
    }
  }
  
  // 分类匹配
  if (item.category && item.category.toLowerCase().includes(query)) {
    score += 25
  }
  
  return score
}

const getMatchedKeywords = (item: SearchItem, query: string): string[] => {
  const matched: string[] = []
  
  if (item.title.toLowerCase().includes(query)) {
    matched.push(query)
  }
  
  if (item.keywords) {
    for (const keyword of item.keywords) {
      if (keyword.toLowerCase().includes(query)) {
        matched.push(keyword)
      }
    }
  }
  
  return matched
}

const handleSearch = () => {
  isSearching.value = true
  selectedIndex.value = 0
  
  // 模拟搜索延迟
  setTimeout(() => {
    isSearching.value = false
  }, 300)
}

const handleKeydown = (event: KeyboardEvent) => {
  switch (event.key) {
    case 'Escape':
      closeSearch()
      break
    case 'ArrowDown':
      event.preventDefault()
      if (selectedIndex.value < filteredResults.value.length - 1) {
        selectedIndex.value++
      }
      break
    case 'ArrowUp':
      event.preventDefault()
      if (selectedIndex.value > 0) {
        selectedIndex.value--
      }
      break
    case 'Enter':
      event.preventDefault()
      if (filteredResults.value.length > 0) {
        selectResult(filteredResults.value[selectedIndex.value])
      }
      break
  }
}

const selectResult = (result: SearchResult) => {
  emit('select', result.item)
  result.item.action()
  closeSearch()
}

const openSearch = () => {
  isVisible.value = true
  searchQuery.value = ''
  selectedIndex.value = 0
  
  nextTick(() => {
    searchInput.value?.focus()
  })
}

const closeSearch = () => {
  isVisible.value = false
  searchQuery.value = ''
  selectedIndex.value = 0
  emit('close')
}

// 暴露方法给父组件
defineExpose({
  openSearch,
  closeSearch
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

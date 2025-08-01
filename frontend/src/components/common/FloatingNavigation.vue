<template>
  <div
    ref="navigationRef"
    class="fixed z-50 select-none bg-white bg-opacity-95 backdrop-blur-md rounded-lg shadow-lg border border-gray-200 transition-all duration-50"
    :class="[
      isCollapsed ? 'w-12 h-12' : 'w-64 max-h-96',
      'cursor-move'
    ]"
    :style="positionStyle"
    @mousedown="startDrag"
    @touchstart="startDrag"
  >
    <!-- 标题栏 -->
    <div
      class="flex items-center justify-between px-3 py-2 bg-gray-50 border-b border-gray-200 rounded-t-lg"
      :class="{ 'justify-center': isCollapsed }"
    >
      <h3
        v-if="!isCollapsed"
        class="text-sm font-medium text-gray-700 truncate"
      >
        {{ title }}
      </h3>

      <!-- 展开/收起按钮 -->
      <button
        @click="toggleCollapse"
        class="p-1 hover:bg-gray-200 rounded transition-colors border-none cursor-pointer"
        :class="{ 'mx-auto': isCollapsed }"
      >
        <ChevronUpIcon
          v-if="!isCollapsed"
          class="h-4 w-4 text-gray-600"
        />
        <ChevronDownIcon
          v-else
          class="h-4 w-4 text-gray-600"
        />
      </button>
    </div>

    <!-- 导航列表 -->
    <div
      v-show="!isCollapsed"
      class="max-h-80 overflow-y-auto"
    >
      <div class="py-2">
        <div
          v-for="(item, index) in navigationItems"
          :key="index"
          @click="scrollToAnchor(item.title)"
          class="px-3 py-2 hover:bg-blue-50 cursor-pointer transition-colors border-b border-gray-100 last:border-b-0"
        >
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-700 truncate">{{ item.title }}</span>
            <ChevronRightIcon class="h-3 w-3 text-gray-400" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ChevronUpIcon, ChevronDownIcon, ChevronRightIcon } from '@heroicons/vue/24/solid'
import { useDraggable } from '@/composable/useDraggable'

// 定义导航项的类型
interface NavigationItem {
  title: string
}

// 组件属性
interface Props {
  title?: string
  navigationItems: NavigationItem[]
  initialPosition?: { x: number; y: number }
}

const props = withDefaults(defineProps<Props>(), {
  title: '导航列表',
  initialPosition: () => ({ x: window.innerWidth - 280, y: 20 })
})

// 响应式数据
const navigationRef = ref<HTMLElement>()
const isCollapsed = ref(false)

// 使用拖拽hook
const { position, positionStyle, startDrag, setEnabled } = useDraggable({
  initialPosition: props.initialPosition,
  boundary: {
    minX: 0,
    minY: 0,
    maxX: window.innerWidth - 256, // 展开时的宽度
    maxY: window.innerHeight - 384  // 展开时的高度
  },
  onDragStart: () => {
    // 拖拽开始时禁用点击事件
  },
  onDragMove: (newPosition) => {
    // 拖拽中更新边界限制
    const maxX = window.innerWidth - (isCollapsed.value ? 48 : 256)
    const maxY = window.innerHeight - (isCollapsed.value ? 48 : 384)

    if (newPosition.x > maxX) {
      newPosition.x = maxX
    }
    if (newPosition.x < 0) {
      newPosition.x = 0
    }
    if (newPosition.y > maxY) {
      newPosition.y = maxY
    }
    if (newPosition.y < 0) {
      newPosition.y = 0
    }
  }
})

// 监听折叠状态变化，更新拖拽启用状态
watch(isCollapsed, (collapsed) => {
  // 折叠时禁用拖拽
  // setEnabled(!collapsed)
})

// 切换展开/收起状态
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

// 滚动到锚点
const scrollToAnchor = (anchor: string) => {
  const element = document.getElementById(anchor)
  if (element) {
    element.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    })
  }
}
</script>

<style scoped>
/* 自定义滚动条样式 */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* 拖拽时的样式 */
.cursor-move:active {
  cursor: grabbing;
}
</style>

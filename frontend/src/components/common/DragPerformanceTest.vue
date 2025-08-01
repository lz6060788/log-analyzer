<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-6">拖拽性能测试</h1>
    
    <!-- 性能测试说明 -->
    <div class="mb-6 p-4 bg-blue-50 rounded-lg">
      <h2 class="text-lg font-semibold mb-2">测试说明</h2>
      <p class="text-sm text-gray-700">
        拖拽以下元素，观察是否还有延迟。优化后的版本应该更加流畅。
      </p>
    </div>

    <!-- 测试元素1：基础拖拽 -->
    <div class="mb-8">
      <h3 class="text-lg font-medium mb-4">基础拖拽测试</h3>
      <div
        class="w-32 h-32 bg-blue-500 rounded-lg cursor-move flex items-center justify-center text-white font-medium"
        :style="draggable1.positionStyle"
        @mousedown="draggable1.startDrag"
        @touchstart="draggable1.startDrag"
      >
        拖拽我
      </div>
      <p class="text-sm text-gray-600 mt-2">
        位置: ({{ Math.round(draggable1.position.x) }}, {{ Math.round(draggable1.position.y) }})
      </p>
    </div>

    <!-- 测试元素2：边界限制拖拽 -->
    <div class="mb-8">
      <h3 class="text-lg font-medium mb-4">边界限制拖拽测试</h3>
      <div class="relative w-96 h-64 bg-gray-100 border-2 border-dashed border-gray-300 rounded-lg">
        <div
          class="w-24 h-24 bg-green-500 rounded-lg cursor-move flex items-center justify-center text-white font-medium absolute"
          :style="draggable2.positionStyle"
          @mousedown="draggable2.startDrag"
          @touchstart="draggable2.startDrag"
        >
          拖拽我
        </div>
      </div>
      <p class="text-sm text-gray-600 mt-2">
        位置: ({{ Math.round(draggable2.position.x) }}, {{ Math.round(draggable2.position.y) }})
      </p>
    </div>

    <!-- 测试元素3：高性能拖拽 -->
    <div class="mb-8">
      <h3 class="text-lg font-medium mb-4">高性能拖拽测试</h3>
      <div
        class="w-40 h-40 bg-purple-500 rounded-lg cursor-move flex items-center justify-center text-white font-medium shadow-lg"
        :style="draggable3.positionStyle"
        @mousedown="draggable3.startDrag"
        @touchstart="draggable3.startDrag"
      >
        流畅拖拽
      </div>
      <p class="text-sm text-gray-600 mt-2">
        位置: ({{ Math.round(draggable3.position.x) }}, {{ Math.round(draggable3.position.y) }})
      </p>
    </div>

    <!-- 性能指标 -->
    <div class="mt-8 p-4 bg-gray-50 rounded-lg">
      <h3 class="text-lg font-medium mb-4">性能优化说明</h3>
      <ul class="text-sm text-gray-700 space-y-2">
        <li>✅ 使用 <code>requestAnimationFrame</code> 优化位置更新</li>
        <li>✅ 使用 <code>transform3d</code> 启用硬件加速</li>
        <li>✅ 添加 <code>willChange: 'transform'</code> 提示浏览器</li>
        <li>✅ 使用 <code>passive: false</code> 优化事件处理</li>
        <li>✅ 添加 <code>backface-visibility: hidden</code> 优化渲染</li>
        <li>✅ 阻止默认行为和事件冒泡</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useDraggable } from '@/composable/useDraggable'

// 基础拖拽测试
const draggable1 = useDraggable({
  initialPosition: { x: 50, y: 50 },
  onDragStart: () => console.log('开始拖拽 1'),
  onDragEnd: (position) => console.log('结束拖拽 1:', position)
})

// 边界限制拖拽测试
const draggable2 = useDraggable({
  initialPosition: { x: 20, y: 20 },
  boundary: {
    minX: 0,
    minY: 0,
    maxX: 288, // 384 - 96
    maxY: 160  // 256 - 96
  },
  onDragStart: () => console.log('开始拖拽 2'),
  onDragEnd: (position) => console.log('结束拖拽 2:', position)
})

// 高性能拖拽测试
const draggable3 = useDraggable({
  initialPosition: { x: 200, y: 200 },
  onDragStart: () => console.log('开始拖拽 3'),
  onDragMove: (position) => {
    // 实时更新位置显示
    console.log('拖拽中 3:', position)
  },
  onDragEnd: (position) => console.log('结束拖拽 3:', position)
})
</script>

<style scoped>
/* 硬件加速优化 */
.fixed, .absolute {
  backface-visibility: hidden;
  perspective: 1000px;
}

/* 拖拽时的样式 */
.cursor-move:active {
  cursor: grabbing;
}
</style> 
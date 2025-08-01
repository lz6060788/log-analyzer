# useDraggable Hook

一个可复用的拖拽功能Hook，提供完整的拖拽交互能力。

## 功能特性

- ✅ 支持鼠标和触摸拖拽
- ✅ 可配置边界限制
- ✅ 支持动态启用/禁用
- ✅ 提供拖拽回调函数
- ✅ 自动清理事件监听器
- ✅ 完整的TypeScript类型支持

## 基本用法

```vue
<template>
  <div
    class="w-32 h-32 bg-blue-500 rounded cursor-move"
    :style="draggable.positionStyle"
    @mousedown="draggable.startDrag"
    @touchstart="draggable.startDrag"
  >
    拖拽我
  </div>
</template>

<script setup lang="ts">
import { useDraggable } from '@/composable/useDraggable'

const draggable = useDraggable({
  initialPosition: { x: 100, y: 100 }
})
</script>
```

## 高级用法

### 边界限制拖拽

```vue
<template>
  <div class="relative w-96 h-64 bg-gray-200 border-2 border-gray-300">
    <div
      class="w-16 h-16 bg-green-500 rounded cursor-move"
      :style="draggable.positionStyle"
      @mousedown="draggable.startDrag"
      @touchstart="draggable.startDrag"
    >
      限制区域
    </div>
  </div>
</template>

<script setup lang="ts">
const draggable = useDraggable({
  initialPosition: { x: 50, y: 50 },
  boundary: {
    minX: 0,
    minY: 0,
    maxX: 320, // 容器宽度 - 元素宽度
    maxY: 192  // 容器高度 - 元素高度
  }
})
</script>
```

### 可控制拖拽

```vue
<template>
  <div>
    <button @click="toggleDraggable">
      {{ draggable.enabled ? '禁用拖拽' : '启用拖拽' }}
    </button>
    <div
      class="w-24 h-24 bg-purple-500 rounded cursor-move"
      :style="draggable.positionStyle"
      @mousedown="draggable.startDrag"
      @touchstart="draggable.startDrag"
    >
      {{ draggable.enabled ? '可拖拽' : '已禁用' }}
    </div>
  </div>
</template>

<script setup lang="ts">
const draggable = useDraggable({
  initialPosition: { x: 200, y: 200 },
  enabled: true
})

const toggleDraggable = () => {
  draggable.setEnabled(!draggable.enabled.value)
}
</script>
```

### 带回调的拖拽

```vue
<template>
  <div
    class="w-20 h-20 bg-red-500 rounded cursor-move"
    :style="draggable.positionStyle"
    @mousedown="draggable.startDrag"
    @touchstart="draggable.startDrag"
  >
    回调
  </div>
</template>

<script setup lang="ts">
const draggable = useDraggable({
  initialPosition: { x: 300, y: 300 },
  onDragStart: () => {
    console.log('开始拖拽')
  },
  onDragMove: (position) => {
    console.log('拖拽中:', position)
  },
  onDragEnd: (position) => {
    console.log('拖拽结束:', position)
  }
})
</script>
```

## API 参考

### 配置参数 (DraggableConfig)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `initialPosition` | `{ x: number; y: number }` | - | 初始位置坐标（必填） |
| `boundary` | `BoundaryConfig` | `undefined` | 边界限制配置 |
| `enabled` | `boolean` | `true` | 是否启用拖拽 |
| `onDragStart` | `() => void` | `undefined` | 拖拽开始回调 |
| `onDragMove` | `(position: Position) => void` | `undefined` | 拖拽中回调 |
| `onDragEnd` | `(position: Position) => void` | `undefined` | 拖拽结束回调 |

### 边界配置 (BoundaryConfig)

```typescript
interface BoundaryConfig {
  minX?: number    // 最小X坐标
  maxX?: number    // 最大X坐标
  minY?: number    // 最小Y坐标
  maxY?: number    // 最大Y坐标
}
```

### 返回值

| 属性 | 类型 | 说明 |
|------|------|------|
| `position` | `ComputedRef<Position>` | 当前位置（响应式） |
| `isDragging` | `ComputedRef<boolean>` | 是否正在拖拽（响应式） |
| `positionStyle` | `ComputedRef<CSSProperties>` | 位置样式对象 |
| `enabled` | `ComputedRef<boolean>` | 是否启用拖拽（响应式） |
| `startDrag` | `(event: MouseEvent \| TouchEvent) => void` | 开始拖拽方法 |
| `setPosition` | `(position: Position) => void` | 设置位置方法 |
| `setEnabled` | `(enabled: boolean) => void` | 设置启用状态方法 |

## 类型定义

```typescript
interface Position {
  x: number
  y: number
}

interface DraggableConfig {
  initialPosition: Position
  boundary?: BoundaryConfig
  enabled?: boolean
  onDragStart?: () => void
  onDragMove?: (position: Position) => void
  onDragEnd?: (position: Position) => void
}

interface BoundaryConfig {
  minX?: number
  maxX?: number
  minY?: number
  maxY?: number
}
```

## 使用技巧

### 1. 动态边界限制

```typescript
const draggable = useDraggable({
  initialPosition: { x: 100, y: 100 },
  onDragMove: (position) => {
    // 根据组件状态动态调整边界
    const maxX = window.innerWidth - (isCollapsed ? 48 : 256)
    const maxY = window.innerHeight - (isCollapsed ? 48 : 384)
    
    if (position.x > maxX) position.x = maxX
    if (position.y > maxY) position.y = maxY
  }
})
```

### 2. 拖拽状态监听

```typescript
import { watch } from 'vue'

const draggable = useDraggable({
  initialPosition: { x: 100, y: 100 }
})

// 监听拖拽状态变化
watch(draggable.isDragging, (isDragging) => {
  if (isDragging) {
    console.log('开始拖拽')
  } else {
    console.log('结束拖拽')
  }
})
```

### 3. 位置持久化

```typescript
import { onMounted } from 'vue'

const draggable = useDraggable({
  initialPosition: { x: 100, y: 100 }
})

// 从localStorage恢复位置
onMounted(() => {
  const savedPosition = localStorage.getItem('draggable-position')
  if (savedPosition) {
    const position = JSON.parse(savedPosition)
    draggable.setPosition(position)
  }
})

// 保存位置到localStorage
watch(draggable.position, (position) => {
  localStorage.setItem('draggable-position', JSON.stringify(position))
})
```

## 注意事项

1. **事件监听器**: Hook会自动管理事件监听器的添加和移除
2. **边界限制**: 如果不设置边界，元素可以拖拽到屏幕外
3. **触摸支持**: 同时支持鼠标和触摸事件
4. **性能优化**: 使用passive: false选项优化触摸事件性能
5. **清理机制**: 组件卸载时自动清理所有事件监听器

## 浏览器兼容性

- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 12+
- ✅ Edge 79+
- ✅ 移动端浏览器

## 示例项目

查看 `DraggableExample.vue` 文件获取完整的使用示例。 
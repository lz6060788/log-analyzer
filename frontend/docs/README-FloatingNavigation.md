# FloatingNavigation 悬浮导航组件

一个可拖拽、可展开收起的悬浮导航列表组件，支持锚点跳转功能。

## 功能特性

- ✅ 悬浮在屏幕右上角
- ✅ 支持鼠标和触摸拖拽
- ✅ 可展开/收起导航列表
- ✅ 点击导航项跳转到对应锚点
- ✅ 响应式设计，适配不同屏幕尺寸
- ✅ 边界限制，防止拖拽出屏幕
- ✅ 平滑滚动动画
- ✅ 自定义滚动条样式

## 使用方法

### 基本用法

```vue
<template>
  <div>
    <!-- 悬浮导航组件 -->
    <FloatingNavigation
      title="页面导航"
      :navigation-items="navigationItems"
    />
    
    <!-- 页面内容 -->
    <section id="section1">
      <h2>第一章</h2>
      <!-- 内容 -->
    </section>
    
    <section id="section2">
      <h2>第二章</h2>
      <!-- 内容 -->
    </section>
  </div>
</template>

<script setup lang="ts">
import FloatingNavigation from './FloatingNavigation.vue'

const navigationItems = [
  { title: '第一章', anchor: 'section1' },
  { title: '第二章', anchor: 'section2' }
]
</script>
```

### 高级用法

```vue
<template>
  <FloatingNavigation
    title="自定义导航"
    :navigation-items="navigationItems"
    :initial-position="{ x: 100, y: 50 }"
  />
</template>

<script setup lang="ts">
const navigationItems = [
  { title: '项目概述', anchor: 'overview' },
  { title: '技术架构', anchor: 'architecture' },
  { title: '功能特性', anchor: 'features' },
  { title: '使用指南', anchor: 'guide' },
  { title: '开发规范', anchor: 'standards' }
]
</script>
```

## Props 属性

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `title` | `string` | `'导航列表'` | 导航组件的标题 |
| `navigationItems` | `NavigationItem[]` | `[]` | 导航项数组，必填 |
| `initialPosition` | `{ x: number; y: number }` | `{ x: window.innerWidth - 280, y: 20 }` | 初始位置坐标 |

## NavigationItem 类型定义

```typescript
interface NavigationItem {
  title: string    // 导航项标题
  anchor: string   // 对应的锚点ID
}
```

## 样式定制

组件使用 Tailwind CSS 样式，可以通过以下方式定制：

### 修改主题色

```vue
<template>
  <FloatingNavigation
    class="custom-navigation"
    :navigation-items="navigationItems"
  />
</template>

<style scoped>
.custom-navigation :deep(.hover\:bg-blue-50:hover) {
  background-color: #fef3c7; /* 自定义悬停颜色 */
}
</style>
```

### 修改尺寸

```vue
<template>
  <FloatingNavigation
    class="large-navigation"
    :navigation-items="navigationItems"
  />
</template>

<style scoped>
.large-navigation :deep(.w-64) {
  width: 20rem; /* 自定义宽度 */
}
</style>
```

## 事件处理

组件内部处理了以下事件：

- `mousedown` / `touchstart`: 开始拖拽
- `mousemove` / `touchmove`: 拖拽中
- `mouseup` / `touchend`: 停止拖拽
- 点击导航项: 滚动到锚点

## 注意事项

1. **锚点ID**: 确保页面中存在对应的锚点元素，ID要与 `NavigationItem.anchor` 匹配
2. **边界限制**: 组件会自动限制在屏幕边界内，防止拖拽出屏幕
3. **响应式**: 组件会根据屏幕尺寸自动调整最大拖拽范围
4. **性能**: 拖拽时会添加全局事件监听器，组件卸载时会自动清理

## 浏览器兼容性

- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 12+
- ✅ Edge 79+

## 示例项目

查看 `FloatingNavigationExample.vue` 文件获取完整的使用示例。 
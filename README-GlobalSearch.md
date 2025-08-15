# 全局搜索功能使用说明

## 功能概述

全局搜索功能允许用户通过快捷键 `Ctrl+K` 快速打开搜索框，搜索并执行各种功能。搜索框悬浮在页面中间偏上的位置，支持模糊搜索和键盘导航。

## 主要特性

- 🚀 **快捷键支持**: 按 `Ctrl+K` 快速打开搜索框
- 🔍 **智能搜索**: 支持标题、描述、关键词、分类的模糊匹配
- ⌨️ **键盘导航**: 支持方向键、Enter、ESC 等快捷键
- 🎨 **美观界面**: 使用 Tailwind CSS 实现的现代化设计
- 🔧 **可配置**: 支持自定义搜索项、配置和样式
- 🌐 **全局可用**: 在应用的任何地方都可以使用

## 使用方法

### 1. 基本使用

搜索框会在应用启动时自动初始化，用户可以直接按 `Ctrl+K` 打开搜索。

### 2. 搜索操作

- **打开搜索**: `Ctrl+K`
- **关闭搜索**: `ESC`
- **选择项目**: `Enter` 或鼠标点击
- **导航**: 上下方向键选择项目

### 3. 注册搜索项

#### 在 App.vue 中注册（推荐）

```typescript
import { useGlobalSearch } from '@/composable/useGlobalSearch'

const { registerSearchItem } = useGlobalSearch()

// 注册单个搜索项
registerSearchItem({
  id: 'custom-action',
  title: '自定义操作',
  description: '执行自定义业务逻辑',
  category: '业务功能',
  keywords: ['自定义', '操作', '业务'],
  action: () => {
    // 执行具体的业务逻辑
    console.log('执行自定义操作')
  }
})
```

#### 在其他组件中注册

```typescript
import { inject } from 'vue'

// 注入全局搜索方法
const registerSearchItem = inject('registerSearchItem') as (item: SearchItem) => void

// 注册搜索项
registerSearchItem({
  id: 'component-action',
  title: '组件操作',
  description: '组件特定的功能',
  category: '组件功能',
  keywords: ['组件', '功能'],
  action: () => {
    // 执行组件特定的逻辑
  }
})
```

### 4. 搜索项配置

每个搜索项支持以下属性：

```typescript
interface SearchItem {
  id: string              // 唯一标识符
  title: string          // 显示标题
  description?: string   // 描述信息
  category?: string      // 分类标签
  icon?: string          // 图标（SVG path）
  keywords?: string[]    // 搜索关键词
  action: () => void     // 点击时执行的动作
}
```

### 5. 搜索配置

可以通过 `updateSearchConfig` 方法更新搜索配置：

```typescript
const { updateSearchConfig } = useGlobalSearch()

updateSearchConfig({
  placeholder: '自定义占位符文本',
  showCategories: true,
  maxResults: 15
})
```

## 组件结构

```
GlobalSearch.vue          # 搜索组件主文件
├── 搜索输入框
├── 搜索结果列表
├── 无结果提示
├── 搜索中状态
└── 默认提示
```

## 样式定制

搜索组件使用 Tailwind CSS 类名，可以通过以下方式定制样式：

1. **修改组件内的 Tailwind 类名**
2. **添加自定义 CSS 样式**
3. **通过 props 传递配置**

## 事件处理

搜索组件会触发以下事件：

- `@close`: 搜索框关闭时触发
- `@select`: 搜索项被选中时触发

```vue
<GlobalSearch
  @close="handleSearchClose"
  @select="handleSearchSelect"
/>
```

## 性能优化

- 搜索结果按匹配度排序
- 支持最大结果数量限制
- 搜索延迟处理，避免频繁搜索
- 组件销毁时自动清理资源

## 注意事项

1. **ID 唯一性**: 确保每个搜索项的 ID 是唯一的
2. **动作函数**: action 函数应该快速执行，避免阻塞 UI
3. **关键词设置**: 合理设置关键词，提高搜索准确性
4. **资源清理**: 在组件销毁时记得移除注册的搜索项

## 示例代码

完整的使用示例请参考：
- `SearchItemExample.vue` - 搜索项注册示例组件
- `App.vue` - 全局搜索集成示例
- `useGlobalSearch.ts` - 组合式函数实现

## 扩展功能

可以根据需要扩展以下功能：

- 搜索历史记录
- 搜索建议
- 高级筛选
- 搜索结果分组
- 自定义搜索算法

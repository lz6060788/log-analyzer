# 模块弹窗系统使用说明

## 功能概述

模块弹窗系统允许用户以弹窗形式打开客户端日志过滤器的各个模块组件，这些模块可以通过全局搜索快速访问，也可以在页面中直接调用。

## 系统架构

### 核心组件

1. **ModuleDialog.vue**: 通用弹窗组件，负责弹窗的显示和基本交互
2. **useModuleManager.ts**: 模块管理器，管理所有可用的模块和它们的元数据
3. **ModuleDemo.vue**: 演示页面，展示如何使用各种模块

### 模块列表

系统预置了以下12个模块：

- **过滤器面板**: 配置和管理日志过滤规则
- **条件面板**: 设置日志过滤的复杂条件
- **算法面板**: 管理和配置算法相关的过滤条件
- **篮子面板**: 配置篮子相关的过滤条件
- **可融资面板**: 设置可融资相关的过滤条件
- **交易面板**: 配置交易相关的过滤条件
- **统计面板**: 查看和分析日志统计信息
- **账户面板**: 管理账户相关的过滤条件
- **基金面板**: 配置基金相关的过滤条件
- **IPO面板**: 设置IPO相关的过滤条件
- **订单面板**: 管理订单相关的过滤条件
- **持仓面板**: 配置持仓相关的过滤条件

## 使用方法

### 1. 通过全局搜索打开模块

1. 按 `Ctrl+K` 打开全局搜索
2. 输入模块名称或关键词（如"过滤器"、"算法"、"交易"等）
3. 选择对应的模块项
4. 模块将以弹窗形式打开

### 2. 在代码中直接调用

```typescript
import { useModuleManager } from '@/composable/useModuleManager'

const { openModule } = useModuleManager()

// 打开特定模块
openModule('filter-panel')      // 打开过滤器面板
openModule('algorithm-panel')   // 打开算法面板
openModule('trade-panel')       // 打开交易面板
```

### 3. 通过依赖注入使用

```typescript
import { inject } from 'vue'

// 在子组件中注入模块打开方法
const openModule = inject('openModule') as (moduleId: string) => void

// 使用注入的方法
openModule('condition-panel')
```

## 弹窗特性

### 界面设计

- **响应式布局**: 支持不同屏幕尺寸，移动端友好
- **现代化设计**: 使用 Tailwind CSS 实现美观的界面
- **清晰的信息层次**: 标题、描述、内容区域分明

### 交互功能

- **ESC 键关闭**: 支持键盘快捷键快速关闭
- **点击遮罩关闭**: 点击弹窗外部区域可关闭弹窗
- **关闭按钮**: 右上角提供明显的关闭按钮
- **滚动支持**: 内容区域支持滚动，适合长内容

### 弹窗尺寸

- **最大宽度**: 4xl (896px)
- **最大高度**: 90vh (视口高度的90%)
- **边距**: 页面边距 16px
- **内边距**: 内容区域 24px

## 模块配置

### 模块元数据

每个模块都包含以下信息：

```typescript
interface ModuleInfo {
  id: string              // 唯一标识符
  title: string          // 显示标题
  description: string    // 功能描述
  category: string       // 分类标签
  icon?: string          // 图标（可选）
  component: Component   // Vue组件
  keywords: string[]     // 搜索关键词
  props?: Record<string, any> // 组件属性
}
```

### 搜索关键词

每个模块都配置了相关的搜索关键词，支持：

- **中文关键词**: 如"过滤器"、"算法"、"交易"
- **英文关键词**: 如"filter"、"algorithm"、"trade"
- **功能描述**: 如"配置"、"管理"、"分析"

## 扩展功能

### 添加新模块

1. 在 `useModuleManager.ts` 中添加模块信息
2. 导入对应的组件
3. 配置模块的元数据和关键词
4. 系统会自动注册到全局搜索中

### 自定义模块属性

可以通过 `props` 字段传递自定义属性给模块组件：

```typescript
{
  id: 'custom-module',
  title: '自定义模块',
  component: CustomComponent,
  props: {
    initialData: someData,
    config: moduleConfig
  }
}
```

## 性能优化

- **懒加载**: 模块组件按需加载
- **事件清理**: 弹窗关闭时自动清理事件监听器
- **内存管理**: 弹窗关闭后释放相关资源

## 注意事项

1. **模块ID唯一性**: 确保每个模块的ID是唯一的
2. **组件兼容性**: 模块组件需要支持 `@close` 事件
3. **响应式设计**: 模块组件应该支持响应式布局
4. **错误处理**: 模块组件应该包含适当的错误处理机制

## 示例代码

完整的使用示例请参考：

- `ModuleDemo.vue` - 模块弹窗演示页面
- `useModuleManager.ts` - 模块管理器实现
- `App.vue` - 全局集成示例

## 故障排除

### 常见问题

1. **模块无法打开**: 检查模块ID是否正确，组件是否正确导入
2. **弹窗不显示**: 确认 `currentModule` 状态是否正确设置
3. **搜索无结果**: 检查模块的关键词配置是否正确

### 调试方法

1. 在浏览器控制台查看相关日志
2. 检查 Vue DevTools 中的组件状态
3. 验证模块组件的导入路径

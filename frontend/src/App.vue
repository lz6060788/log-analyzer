<template>
  <div class="bg-gray-100 min-h-screen" id="container-wrapper">
    <RouterView />

    <!-- 全局搜索组件 -->
    <GlobalSearch
      ref="searchComponentRef"
      :items="searchItems"
      :config="searchConfig"
      @close="handleSearchClose"
      @select="handleSearchSelect"
    />

    <!-- 模块弹窗 -->
    <ModuleDialog
      v-if="currentModule"
      ref="moduleDialogRef"
      :title="currentModule.title"
      :description="currentModule.description"
      :module-component="currentModule.component"
      :module-props="currentModule.props"
      @close="handleModuleClose"
    />
  </div>
</template>

<script lang="ts" setup>
import { RouterView } from 'vue-router'
import { ref, onMounted, onUnmounted, provide, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import GlobalSearch from '@/components/common/GlobalSearch.vue'
import { useGlobalSearch } from '@/composable/useGlobalSearch'
import { useModuleManager } from '@/composable/useModuleManager'
import type { SearchItem } from '@/types/search'
import { defineAsyncComponent } from 'vue'

const ModuleDialog = defineAsyncComponent(() =>
  import('@/components/common/ModuleDialog.vue')
)

// 使用全局搜索组合式函数
const {
  searchItems,
  searchConfig,
  searchComponentRef,
  registerSearchItem,
  openSearch,
  initialize,
  destroy
} = useGlobalSearch()

// 使用模块管理器
const {
  currentModule,
  moduleDialogRef,
  availableModules,
  openModule,
  closeModule,
  getModuleSearchItems,
  setModuleDialogRef
} = useModuleManager()

// 为子组件提供方法
provide('openSearch', openSearch)
provide('openModule', openModule)
provide('currentModule', currentModule)
provide('moduleDialogRef', moduleDialogRef)
provide('availableModules', availableModules)

// 搜索事件处理
const handleSearchClose = () => {
  // 搜索框关闭时的处理逻辑
  console.log('搜索框已关闭')
}

const handleSearchSelect = (item: SearchItem) => {
  // 搜索项被选中时的处理逻辑
  console.log('选中搜索项:', item.title)
  ElMessage.success(`已选择: ${item.title}`)
}

// 模块事件处理
const handleModuleClose = () => {
  closeModule()
}

// 生命周期钩子
onMounted(async () => {
  // 初始化全局搜索
  initialize()
  
  // 等待下一个tick，确保DOM已经渲染
  await nextTick()
  
  // 设置模块弹窗引用
  if (moduleDialogRef.value) {
    setModuleDialogRef(moduleDialogRef.value)
  }
  
  // 注册模块搜索项
  const moduleSearchItems = getModuleSearchItems()
  moduleSearchItems.forEach(item => {
    registerSearchItem(item)
  })
})

onUnmounted(() => {
  // 销毁全局搜索
  destroy()
})
</script>

<style scoped>
</style>

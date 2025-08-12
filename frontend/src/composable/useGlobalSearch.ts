import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import hotkeys from 'hotkeys-js'
import type { SearchItem, SearchConfig } from '@/types/search'

/**
 * 全局搜索组合式函数
 */
export function useGlobalSearch() {
  const router = useRouter()
  
  // 搜索项列表
  const searchItems = ref<SearchItem[]>([])
  
  // 搜索配置
  const searchConfig = reactive<SearchConfig>({
    placeholder: '搜索功能、页面、操作...',
    showCategories: true,
    maxResults: 10
  })
  
  // 搜索组件引用
  const searchComponentRef = ref<{ openSearch: () => void }>()
  
  /**
   * 注册搜索项
   */
  const registerSearchItem = (item: SearchItem) => {
    // 检查是否已存在相同ID的搜索项
    const existingIndex = searchItems.value.findIndex(existing => existing.id === item.id)
    if (existingIndex !== -1) {
      // 更新现有项
      searchItems.value[existingIndex] = item
    } else {
      // 添加新项
      searchItems.value.push(item)
    }
  }
  
  /**
   * 批量注册搜索项
   */
  const registerSearchItems = (items: SearchItem[]) => {
    items.forEach(item => registerSearchItem(item))
  }
  
  /**
   * 移除搜索项
   */
  const removeSearchItem = (id: string) => {
    const index = searchItems.value.findIndex(item => item.id === id)
    if (index !== -1) {
      searchItems.value.splice(index, 1)
    }
  }
  
  /**
   * 清空所有搜索项
   */
  const clearSearchItems = () => {
    searchItems.value = []
  }
  
  /**
   * 更新搜索配置
   */
  const updateSearchConfig = (config: Partial<SearchConfig>) => {
    Object.assign(searchConfig, config)
  }
  
  /**
   * 打开搜索框
   */
  const openSearch = () => {
    searchComponentRef.value?.openSearch()
  }
  
  /**
   * 关闭搜索框
   */
  const closeSearch = () => {
    // 搜索组件会自动处理关闭逻辑
  }
  
  /**
   * 初始化默认搜索项
   */
  const initializeDefaultSearchItems = () => {
    const defaultItems: SearchItem[] = [
      {
        id: 'home',
        title: '首页',
        description: '返回应用首页',
        category: '导航',
        keywords: ['首页', '主页', 'home', 'main'],
        action: () => router.push('/')
      },
      {
        id: 'client-log',
        title: '客户端日志',
        description: '查看和分析客户端日志数据',
        category: '日志分析',
        keywords: ['客户端', '日志', 'client', 'log', '分析'],
        action: () => router.push('/client-log')
      },
      {
        id: 'operation-log',
        title: '操作日志',
        description: '查看系统操作日志',
        category: '日志分析',
        keywords: ['操作', '日志', 'operation', 'log', '系统'],
        action: () => router.push('/operation-log')
      },
      {
        id: 'log-paste',
        title: '日志粘贴',
        description: '粘贴并分析日志内容',
        category: '日志分析',
        keywords: ['粘贴', '日志', 'paste', 'log', '分析'],
        action: () => router.push('/log-paste')
      },
      {
        id: 'log-pool',
        title: '日志池',
        description: '查看日志池中的历史记录',
        category: '日志分析',
        keywords: ['日志池', '历史', 'pool', 'history'],
        action: () => router.push('/log-pool')
      }
    ]
    
    registerSearchItems(defaultItems)
  }
  
  /**
   * 绑定快捷键
   */
  const bindHotkeys = () => {
    // 绑定 Ctrl+K 快捷键
    hotkeys('ctrl+k, cmd+k', (event) => {
      event.preventDefault()
      openSearch()
    })
    
    // 绑定 ESC 快捷键（在搜索组件中处理）
    hotkeys('escape', (event) => {
      // 这里不需要阻止默认行为，让搜索组件处理
    })
  }
  
  /**
   * 解绑快捷键
   */
  const unbindHotkeys = () => {
    hotkeys.unbind('ctrl+k, cmd+k')
    hotkeys.unbind('escape')
  }
  
  /**
   * 初始化全局搜索
   */
  const initialize = () => {
    initializeDefaultSearchItems()
    bindHotkeys()
  }
  
  /**
   * 销毁全局搜索
   */
  const destroy = () => {
    unbindHotkeys()
    clearSearchItems()
  }
  
  return {
    // 状态
    searchItems,
    searchConfig,
    searchComponentRef,
    
    // 方法
    registerSearchItem,
    registerSearchItems,
    removeSearchItem,
    clearSearchItems,
    updateSearchConfig,
    openSearch,
    closeSearch,
    initialize,
    destroy
  }
}

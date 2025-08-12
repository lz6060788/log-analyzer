import { ref, reactive } from 'vue'
import type { Component } from 'vue'

// 直接导入所有模块组件
import FilterPanel from '../components/clientLogFilter/filterPanel.vue'
import ConditionPanel from '../components/clientLogFilter/conditionPanel.vue'
import AlgorithmPanel from '../components/clientLogFilter/algorithmPanel.vue'
import BasketPanel from '../components/clientLogFilter/basketPanel.vue'
import FinablePanel from '../components/clientLogFilter/finablePanel.vue'
import TradePanel from '../components/clientLogFilter/tradePanel.vue'
import StatisticPanel from '../components/clientLogFilter/statisticPanel.vue'
import AccountsPanel from '../components/clientLogFilter/accountsPanel.vue'
import FundPanel from '../components/clientLogFilter/fundPanel.vue'
import IpoPanel from '../components/clientLogFilter/ipoPanel.vue'
import OrderPanel from '../components/clientLogFilter/orderPanel.vue'
import PositionPanel from '../components/clientLogFilter/positionPanel.vue'

/**
 * 模块信息接口
 */
export interface ModuleInfo {
  /** 模块ID */
  id: string
  /** 模块标题 */
  title: string
  /** 模块描述 */
  description: string
  /** 模块分类 */
  category: string
  /** 模块图标 */
  icon?: string
  /** 模块组件 */
  component: Component
  /** 搜索关键词 */
  keywords: string[]
  /** 模块属性 */
  props?: Record<string, any>
}

/**
 * 模块管理器组合式函数
 */
export function useModuleManager() {
  // 所有可用模块
  const availableModules = reactive<ModuleInfo[]>([
    {
      id: 'filter-panel',
      title: '过滤器面板',
      description: '配置和管理日志过滤规则',
      category: '日志分析',
      keywords: ['过滤器', '过滤', '规则', '配置', 'filter', 'panel'],
      component: FilterPanel
    },
    {
      id: 'condition-panel',
      title: '条件面板',
      description: '设置日志过滤的复杂条件',
      category: '日志分析',
      keywords: ['条件', '条件面板', '复杂条件', 'condition', 'panel'],
      component: ConditionPanel
    },
    {
      id: 'algorithm-panel',
      title: '算法面板',
      description: '管理和配置算法相关的过滤条件',
      category: '日志分析',
      keywords: ['算法', '算法面板', 'algorithm', 'panel'],
      component: AlgorithmPanel
    },
    {
      id: 'basket-panel',
      title: '股票篮子面板',
      description: '配置篮子相关的过滤条件',
      category: '日志分析',
      keywords: ['篮子', '篮子面板', 'basket', 'panel'],
      component: BasketPanel
    },
    {
      id: 'finable-panel',
      title: '可融资面板',
      description: '融资可用查询相关的过滤条件',
      category: '日志分析',
      keywords: ['融资可用', '融资可用查询', 'finable', 'panel'],
      component: FinablePanel
    },
    {
      id: 'trade-panel',
      title: '交易面板',
      description: '交易查询相关的过滤条件',
      category: '日志分析',
      keywords: ['交易', '交易面板', 'trade', 'panel'],
      component: TradePanel
    },
    {
      id: 'statistic-panel',
      title: '统计面板',
      description: '查看和分析日志统计信息',
      category: '日志分析',
      keywords: ['统计', '统计面板', 'statistic', 'panel'],
      component: StatisticPanel
    },
    {
      id: 'accounts-panel',
      title: '资金账户面板',
      description: '管理资金账户相关的过滤条件',
      category: '日志分析',
      keywords: ['资金账户', '资金账户面板', 'accounts', 'panel'],
      component: AccountsPanel
    },
    {
      id: 'fund-panel',
      title: '资金面板',
      description: '资金查询相关的过滤条件',
      category: '日志分析',
      keywords: ['资金', '资金面板', 'fund', 'panel'],
      component: FundPanel
    },
    {
      id: 'ipo-panel',
      title: '新股申购面板',
      description: '设置新股申购相关的过滤条件',
      category: '日志分析',
      keywords: ['新股申购', '新股申购面板', 'ipo', 'panel'],
      component: IpoPanel
    },
    {
      id: 'order-panel',
      title: '订单面板',
      description: '管理订单相关的过滤条件',
      category: '日志分析',
      keywords: ['订单', '订单面板', 'order', 'panel'],
      component: OrderPanel
    },
    {
      id: 'position-panel',
      title: '持仓面板',
      description: '配置持仓相关的过滤条件',
      category: '日志分析',
      keywords: ['持仓', '持仓面板', 'position', 'panel'],
      component: PositionPanel
    }
  ])

  // 当前打开的模块
  const currentModule = ref<ModuleInfo | null>(null)
  
  // 模块弹窗引用
  const moduleDialogRef = ref<{ openDialog: () => void }>()

  /**
   * 设置模块弹窗引用
   */
  const setModuleDialogRef = (ref: { openDialog: () => void }) => {
    moduleDialogRef.value = ref
    console.log('模块弹窗引用已设置:', ref)
  }

  /**
   * 根据ID获取模块信息
   */
  const getModuleById = (id: string): ModuleInfo | undefined => {
    return availableModules.find(module => module.id === id)
  }

  /**
   * 根据关键词搜索模块
   */
  const searchModules = (query: string): ModuleInfo[] => {
    const lowerQuery = query.toLowerCase()
    return availableModules.filter(module => {
      // 标题匹配
      if (module.title.toLowerCase().includes(lowerQuery)) return true
      // 描述匹配
      if (module.description.toLowerCase().includes(lowerQuery)) return true
      // 关键词匹配
      if (module.keywords.some(keyword => keyword.toLowerCase().includes(lowerQuery))) return true
      // 分类匹配
      if (module.category.toLowerCase().includes(lowerQuery)) return true
      return false
    })
  }

  /**
   * 打开模块
   */
  const openModule = (moduleId: string) => {
    console.log('openModule', moduleId)
    const module = getModuleById(moduleId)
    if (module) {
      console.log('module', module)
      console.log('moduleDialogRef', moduleDialogRef.value)
      currentModule.value = module
      
      // 等待下一个tick，确保DOM更新
      setTimeout(() => {
        if (moduleDialogRef.value) {
          moduleDialogRef.value.openDialog()
        } else {
          console.error('模块弹窗引用未设置')
        }
      }, 0)
    }
  }

  /**
   * 关闭模块
   */
  const closeModule = () => {
    currentModule.value = null
  }

  /**
   * 获取所有模块的搜索项（用于全局搜索）
   */
  const getModuleSearchItems = () => {
    return availableModules.map(module => ({
      id: `module-${module.id}`,
      title: module.title,
      description: module.description,
      category: module.category,
      keywords: module.keywords,
      action: () => openModule(module.id)
    }))
  }

  return {
    // 状态
    availableModules,
    currentModule,
    moduleDialogRef,
    
    // 方法
    getModuleById,
    searchModules,
    openModule,
    closeModule,
    getModuleSearchItems,
    setModuleDialogRef
  }
}

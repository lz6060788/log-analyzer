/**
 * 搜索项接口
 */
export interface SearchItem {
  /** 搜索项的唯一标识 */
  id: string
  /** 搜索项标题 */
  title: string
  /** 搜索项描述 */
  description?: string
  /** 搜索项分类 */
  category?: string
  /** 搜索项图标 */
  icon?: string
  /** 点击时执行的动作 */
  action: () => void
  /** 搜索关键词，用于匹配 */
  keywords?: string[]
}

/**
 * 搜索配置接口
 */
export interface SearchConfig {
  /** 搜索框占位符 */
  placeholder?: string
  /** 是否显示分类标签 */
  showCategories?: boolean
  /** 最大显示结果数量 */
  maxResults?: number
}

/**
 * 搜索结果接口
 */
export interface SearchResult {
  /** 匹配的搜索项 */
  item: SearchItem
  /** 匹配度分数 */
  score: number
  /** 匹配的关键词 */
  matchedKeywords: string[]
}

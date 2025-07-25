/**
 * 日志字段类型
 */
export interface ParsedLogField {
  /** 字段内容 */
  value: string;
  /** 是否为高亮字段 */
  highlight?: boolean;
  /** 字段类型（如时间、json等） */
  type?: 'time' | 'json' | 'normal';
}

/**
 * 解析后的一条日志
 */
export interface ParsedLogLine {
  /** 原始日志行 */
  raw: string;
  /** 解析后的字段 */
  fields: ParsedLogField[];
  /** 是否包含JSON */
  hasJson: boolean;
  /** 匹配到的JSON字符串（如有） */
  jsonStr?: string;
  /**
   * 匹配到的UUID（如有）
   * 如 6dd8b4d7-abc2-0861-8be9-c5bb931a62fd
   */
  uuid?: string;
  /**
   * 匹配到的method（如有）
   * 如 method: "xxxx"
   */
  method?: string;
} 

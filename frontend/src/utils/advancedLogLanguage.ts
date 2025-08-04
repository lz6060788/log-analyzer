import * as monaco from 'monaco-editor';

/**
 * 高级日志语言定义
 * 支持更复杂的日志格式和更精确的语法高亮
 */
export const advancedLogLanguageDefinition: monaco.languages.IMonarchLanguage = {
  // 定义语言标识符
  tokenizer: {
    root: [
      // 时间戳匹配 (多种格式)
      [/\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d{3})?/, 'timestamp'],
      [/\d{2}:\d{2}:\d{2}(?:\.\d{3})?/, 'timestamp'],

      // UUID匹配 (更精确)
      [/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i, 'uuid'],

      // 日志级别匹配 (支持大小写)
      [/\b(ERROR|WARN|INFO|DEBUG|TRACE|error|warn|info|debug|trace)\b/, 'logLevel'],

      // HTTP方法匹配
      [/\b(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\b/, 'httpMethod'],

      // HTTP状态码匹配
      [/\b(200|201|204|400|401|403|404|500|502|503)\b/, 'httpStatus'],

      // IP地址匹配
      [/\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/, 'ipAddress'],

      // 端口号匹配
      [/:\d{4,5}/, 'port'],

      // 文件路径匹配
      [/\/[^\s|]+/, 'filePath'],

      // 类名匹配 (如: com.example.ClassName)
      [/\b[a-zA-Z_$][a-zA-Z0-9_$]*\.[a-zA-Z_$][a-zA-Z0-9_$]*\b/, 'className'],

      // 方法名匹配
      [/\b[a-zA-Z_$][a-zA-Z0-9_$]*\(/, 'methodName'],

      // 异常类型匹配
      [/\b(?:Exception|Error|RuntimeException|IOException)\b/, 'exceptionType'],

      // 数字匹配 (包括小数)
      [/\b\d+\.\d+\b/, 'decimal'],
      [/\b\d+\b/, 'number'],

      // 管道分隔符
      [/\|/, 'separator'],

      // 等号
      [/=/, 'operator'],

      // 引号内的字符串
      [/"[^"]*"/, 'string'],
      [/'[^']*'/, 'string'],

      // JSON对象匹配 (更精确)
      [/\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}/, 'json'],

      // 数组匹配
      [/\[[^\]]*\]/, 'array'],

      // 其他字符
      [/./, 'text']
    ]
  }
};

/**
 * 注册高级日志语言
 */
export function registerAdvancedLogLanguage() {
  // 注册语言
  monaco.languages.register({ id: 'advanced-log' });
  
  // 设置语言配置
  monaco.languages.setMonarchTokensProvider('advanced-log', advancedLogLanguageDefinition);
  
  // 设置语言配置选项
  monaco.languages.setLanguageConfiguration('advanced-log', {
    comments: {
      lineComment: '#',
      blockComment: ['/*', '*/']
    },
    brackets: [
      ['{', '}'],
      ['[', ']'],
      ['(', ')']
    ],
    autoClosingPairs: [
      { open: '{', close: '}' },
      { open: '[', close: ']' },
      { open: '(', close: ')' },
      { open: '"', close: '"' },
      { open: "'", close: "'" }
    ],
    surroundingPairs: [
      { open: '{', close: '}' },
      { open: '[', close: ']' },
      { open: '(', close: ')' },
      { open: '"', close: '"' },
      { open: "'", close: "'" }
    ]
  });
}

/**
 * 定义高级日志主题颜色
 */
export const advancedLogTheme: monaco.editor.IStandaloneThemeData = {
  base: 'vs-dark',
  inherit: true,
  rules: [
    // 时间戳 - 蓝色加粗
    { token: 'timestamp', foreground: '569CD6', fontStyle: 'bold' },
    
    // UUID - 青色
    { token: 'uuid', foreground: '4EC9B0' },
    
    // 日志级别 - 不同颜色
    { token: 'logLevel', foreground: 'DCDCAA' },
    { token: 'logLevel.ERROR', foreground: 'F44747', fontStyle: 'bold' },
    { token: 'logLevel.WARN', foreground: 'FFA500', fontStyle: 'bold' },
    { token: 'logLevel.INFO', foreground: '4EC9B0' },
    { token: 'logLevel.DEBUG', foreground: '569CD6' },
    { token: 'logLevel.TRACE', foreground: '808080' },
    
    // HTTP相关 - 橙色
    { token: 'httpMethod', foreground: 'D7BA7D' },
    { token: 'httpStatus', foreground: 'CE9178' },
    
    // 网络相关 - 绿色
    { token: 'ipAddress', foreground: '6A9955' },
    { token: 'port', foreground: '6A9955' },
    
    // 文件路径 - 紫色
    { token: 'filePath', foreground: 'C586C0' },
    
    // 类名和方法 - 黄色
    { token: 'className', foreground: 'DCDCAA' },
    { token: 'methodName', foreground: 'DCDCAA' },
    
    // 异常 - 红色
    { token: 'exceptionType', foreground: 'F44747' },
    
    // 数字 - 浅绿色
    { token: 'number', foreground: 'B5CEA8' },
    { token: 'decimal', foreground: 'B5CEA8' },
    
    // JSON - 浅蓝色
    { token: 'json', foreground: '9CDCFE' },
    
    // 数组 - 浅紫色
    { token: 'array', foreground: 'C586C0' },
    
    // 字符串 - 橙色
    { token: 'string', foreground: 'CE9178' },
    
    // 分隔符和操作符 - 灰色
    { token: 'separator', foreground: '808080' },
    { token: 'operator', foreground: 'D4D4D4' },
    
    // 普通文本 - 白色
    { token: 'text', foreground: 'D4D4D4' }
  ],
  colors: {
    'editor.background': '#1E1E1E',
    'editor.foreground': '#D4D4D4'
  }
};

/**
 * 注册高级日志主题
 */
export function registerAdvancedLogTheme() {
  monaco.editor.defineTheme('advanced-log-theme', advancedLogTheme);
} 
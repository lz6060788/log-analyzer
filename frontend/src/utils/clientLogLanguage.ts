import * as monaco from 'monaco-editor';

/**
 * 自定义日志语言定义
 * 定义日志文件的语法高亮规则
 */
export const clientLogLanguageDefinition: monaco.languages.IMonarchLanguage = {
  // 定义语言标识符
  tokenizer: {
    root: [
      // 时间戳匹配 (如: 2024-01-27 10:30:45.123)
      [/\d{4}\d{2}\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d{3})?/, 'timestamp'],

      // UUID匹配
      [/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i, 'uuid'],

      // 日志级别匹配 - 分别匹配不同的级别
      [/\berror|timeout\b/, 'logLevel.error'],
      [/\bwarn\b/, 'logLevel.warn'],
      [/\binfo\b/, 'logLevel.info'],
      [/\bdebug\b/, 'logLevel.debug'],
      [/\btrace\b/, 'logLevel.trace'],

      // 方法
      [/"method"\s*:\s*"([^"]+)"/, 'method'],

      // action值匹配 (匹配action键值对中的值部分) - 高优先级
      [/"action"\s*:\s*"([^"]+)"/, 'actionValue'],

      // request
      [/request/, 'request'],

      // response
      [/response/, 'response'],

      // // JSON对象匹配 (贪心匹配，支持嵌套)
      // [/\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}/, 'json'],

      // 引号内的字符串 (低优先级，避免覆盖特定规则)
      [/"[^"]*"/, 'string'],

      // 管道分隔符
      [/\|/, 'separator'],

      // 数字
      [/\b\d+\b/, 'number'],

      // 其他字符
      [/./, 'text']
    ]
  }
};

/**
 * 注册自定义日志语言
 */
export function registerClientLogLanguage() {
  // 注册语言
  monaco.languages.register({ id: 'client-log' });

  // 设置语言配置
  monaco.languages.setMonarchTokensProvider('client-log', clientLogLanguageDefinition);

  // 设置语言配置选项
  monaco.languages.setLanguageConfiguration('client-log', {
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
 * 定义日志主题颜色
 */
export const clientLogTheme: monaco.editor.IStandaloneThemeData = {
  base: 'vs-dark',
  inherit: true,
  rules: [
    { token: 'timestamp', foreground: '569CD6', fontStyle: 'bold' },
    { token: 'uuid', foreground: '4EC9B0' },
    { token: 'logLevel', foreground: 'DCDCAA' },
    { token: 'logLevel.error', foreground: 'F44747' },
    { token: 'logLevel.warn', foreground: 'FFA500' },
    { token: 'logLevel.info', foreground: '4EC9B0' },
    { token: 'logLevel.debug', foreground: '569CD6' },
    { token: 'logLevel.trace', foreground: '569CD6' },
    { token: 'string', foreground: 'CE9178' },
    { token: 'json', foreground: '9CDCFE' },
    { token: 'method', foreground: 'D7BA7D' },
    { token: 'actionValue', foreground: 'FFD700' },
    { token: 'separator', foreground: '808080' },
    { token: 'number', foreground: 'B5CEA8' },
    { token: 'text', foreground: 'D4D4D4' },
    { token: 'request', foreground: 'FFDD00' },
    { token: 'response', foreground: '4EC9B0' }
  ],
  colors: {
    'editor.background': '#1E1E1E',
    'editor.foreground': '#D4D4D4'
  }
};

/**
 * 注册日志主题
 */
export function registerClientLogTheme() {
  monaco.editor.defineTheme('client-log-theme', clientLogTheme);
}
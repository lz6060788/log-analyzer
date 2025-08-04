import type { ParsedLogLine, ParsedLogField } from '../types/logParser';

/**
 * 解析一段 client 类日志文本为日志行对象数组
 * @param logText 粘贴的原始日志文本
 * @returns 解析后的日志行数组
 */
export function parseClientLogLines(logText: string): ParsedLogLine[] {
  if (!logText) return [];
  const lines = logText.split(/\r?\n/).filter(Boolean);
  return lines.map(parseClientLogLine);
}

/**
 * 按规则分割日志行，忽略花括号内的分隔符
 * @param line 日志行
 * @returns 字段数组
 */
function smartSplit(line: string): string[] {
  const result: string[] = [];
  let buf = '';
  let braceLevel = 0;
  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    if (char === '{') braceLevel++;
    if (char === '}') braceLevel = Math.max(0, braceLevel - 1);
    if (char === '|' && braceLevel === 0) {
      result.push(buf);
      buf = '';
    } else {
      buf += char;
    }
  }
  if (buf) result.push(buf);
  return result;
}

/**
 * 解析单行 client 类日志
 * @param line 单行日志
 * @returns 解析后的日志对象
 */
export function parseClientLogLine(line: string): ParsedLogLine {
  // 提取uuid
  const uuidReg = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i;
  const uuidMatch = line.match(uuidReg);
  const uuid = uuidMatch ? uuidMatch[0] : undefined;

  // 提取method
  const methodReg = /"method"\s*:\s*"([^"]+)"/;
  const methodMatch = line.match(methodReg);
  const method = methodMatch ? methodMatch[1] : undefined;

  // 使用smartSplit分割字段
  const fields = smartSplit(line).map((field, idx) => {
    // 检查是否为时间字段（如 2023-01-01 12:00:00.000）
    const timeReg = /\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}/;
    const isTime = timeReg.test(field);
    // 检查是否为 JSON
    let isJson = false;
    try {
      const json = JSON.parse(field);
      isJson = typeof json === 'object';
    } catch {}
    return {
      value: field.trim(),
      highlight: isTime,
      type: isTime ? 'time' : isJson ? 'json' : 'normal',
    } as ParsedLogField;
  });

  // 检查整行是否包含 JSON 字符串
  const jsonReg = /({[\s\S]*})/;
  const jsonMatch = line.match(jsonReg);
  const hasJson = !!jsonMatch;
  return {
    raw: line,
    fields,
    hasJson,
    jsonStr: hasJson ? jsonMatch![1] : undefined,
    uuid,
    method,
  };
}

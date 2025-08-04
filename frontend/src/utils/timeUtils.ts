/**
 * 时间工具函数
 * 用于处理不同格式的时间字符串解析
 */

/**
 * 解析时间字符串为时间戳
 * @param timeStr 时间字符串
 * @returns 时间戳（毫秒）
 */
export const parseTimeToTimestamp = (timeStr: string, type: 'client' | 'operation'): number => {
  // 处理 clientLogList 的时间格式: 20250415 09:02:33.104
  if (type === 'client') {
    const [datePart, timePart] = timeStr.split(' ')
    const year = datePart.substring(0, 4)
    const month = datePart.substring(4, 6)
    const day = datePart.substring(6, 8)
    // const [time, milliseconds] = timePart.split('.')
    // const [hour, minute, second] = time.split(':')

    return new Date(`${year}-${month}-${day}T${timePart}`).getTime()
  }

  // 处理 operationLogList 的时间格式: 20250415 09:18:39:730:830
  if (type === 'operation') {
    const [datePart, timePart] = timeStr.split(' ')
    const parts = timePart.split(':')
    const hour = parts[0]
    const minute = parts[1]
    const second = parts[2]
    const milliseconds = parts[3] || '000'

    const year = datePart.substring(0, 4)
    const month = datePart.substring(4, 6)
    const day = datePart.substring(6, 8)

    return new Date(`${year}-${month}-${day}T${hour}:${minute}:${second}.${milliseconds}`).getTime()
  }

  // 如果格式不匹配，返回0（排在最后）
  return 0
}

/**
 * 使用双指针方法合并两个有序数组
 * @param arr1 第一个有序数组
 * @param arr2 第二个有序数组
 * @param compareFn 比较函数
 * @returns 合并后的有序数组
 */
export const mergeSortedArrays = <T>(
  arr1: T[],
  arr2: T[],
  compareFn: (a: T, b: T) => number
): T[] => {
  const result: T[] = []
  let i = 0 // arr1 的指针
  let j = 0 // arr2 的指针
  
  // 双指针遍历，选择较小的元素
  while (i < arr1.length && j < arr2.length) {
    if (compareFn(arr1[i], arr2[j]) <= 0) {
      result.push(arr1[i])
      i++
    } else {
      result.push(arr2[j])
      j++
    }
  }
  
  // 处理剩余元素
  while (i < arr1.length) {
    result.push(arr1[i])
    i++
  }
  
  while (j < arr2.length) {
    result.push(arr2[j])
    j++
  }
  
  return result
} 
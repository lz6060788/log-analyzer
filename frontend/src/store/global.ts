import { LogAnalyserType, LogAnalyserStatusType } from '@/types'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useGlobalStore = defineStore('global', () => {
  const logAnalyserStatusMap = ref<Record<LogAnalyserType, LogAnalyserStatusType>>({
    [LogAnalyserType.Client]: LogAnalyserStatusType.None,
    [LogAnalyserType.Operation]: LogAnalyserStatusType.None
  })

  const setLogAnalyserStatus = (type: LogAnalyserType, status: LogAnalyserStatusType) => {
    logAnalyserStatusMap.value[type] = status
  }

  const getLogAnalyserStatus = (type: LogAnalyserType) => {
    return logAnalyserStatusMap.value[type]
  }

  return {
    logAnalyserStatusMap,
    setLogAnalyserStatus,
    getLogAnalyserStatus
  }
})

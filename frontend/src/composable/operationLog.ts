import { operationLogApi } from '@/api';
import { useGlobalStore } from '@/store/global';
import { LogAnalyserType, LogAnalyserStatusType } from '@/types';
import { ElNotification } from 'element-plus'
import { computed, ref } from 'vue';
import { storeToRefs } from 'pinia'


export const useOperationLogAnalyser = () => {
  const store = useGlobalStore()
  const { setLogAnalyserStatus, getLogAnalyserStatus } = store
  const { logAnalyserStatusMap } = storeToRefs(store)
  const operationLogAnalyserStatus = computed(() => logAnalyserStatusMap.value[LogAnalyserType.Operation])

  const initOperationLogAnalyser = async (files: File[]) => {
    setLogAnalyserStatus(LogAnalyserType.Operation, LogAnalyserStatusType.None)
    try {
      setLogAnalyserStatus(LogAnalyserType.Operation, LogAnalyserStatusType.Running)
      const res = await operationLogApi.uploadOperationLog(files)
      if (res.code === 0) {
        ElNotification.success({
          title: '提示',
          message: `客户端操作日志已上传并解析成功，共上传 ${files.length} 个文件`,
        })
        setLogAnalyserStatus(LogAnalyserType.Operation, LogAnalyserStatusType.Ready)
      } else {
        setLogAnalyserStatus(LogAnalyserType.Operation, LogAnalyserStatusType.Error)
        throw new Error(res.message)
      }
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const filterLogList = async (data?: {content?: string, startTime?: string, endTime?: string}) => {
    if (!checkoutOperationLogAnalyserStatus()) {
      return [];
    }
    try {
      const res = await operationLogApi.filterLogList(data)
      if (res.code !== 0) {
        throw new Error(res.message)
      }
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  function checkoutOperationLogAnalyserStatus () {
    // if (getLogAnalyserStatus(LogAnalyserType.Operation) === LogAnalyserStatusType.None) {
    //   ElNotification.error({
    //     title: 'Error',
    //     message: '操作日志未解析完成',
    //   })
    //   return false;
    // }
    return true
  }

  return {
    checkoutOperationLogAnalyserStatus,
    operationLogAnalyserStatus,
    initOperationLogAnalyser,
    filterLogList
  }
}

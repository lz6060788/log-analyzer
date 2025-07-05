import { clientLogApi } from '@/api';
import { useGlobalStore } from '@/store/global';
import { LogAnalyserType, LogAnalyserStatusType } from '@/types';
import { ElNotification } from 'element-plus'

const { setLogAnalyserStatus, getLogAnalyserStatus } = useGlobalStore()
export const useClientLogAnalyser = () => {
  const initClientLogAnalyser = async (file: File) => {
    setLogAnalyserStatus(LogAnalyserType.Client, LogAnalyserStatusType.None)
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await clientLogApi.uploadClientLog(formData)
      if (res.status === 200) {
        setLogAnalyserStatus(LogAnalyserType.Client, LogAnalyserStatusType.Ready)
      } else {
        setLogAnalyserStatus(LogAnalyserType.Client, LogAnalyserStatusType.Error)
        throw new Error(res.data.message)
      }
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const getAccountsLogs = async () => {
    if (getLogAnalyserStatus(LogAnalyserType.Client) === LogAnalyserStatusType.None) {
      ElNotification.error({
        title: 'Error',
        message: '全量日志未解析完成',
      })
    }
    try {
      const res = await clientLogApi.getAccountsQuery()
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  return {
    initClientLogAnalyser,
    getAccountsLogs
  }
}

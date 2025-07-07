import { clientLogApi } from '@/api';
import { useGlobalStore } from '@/store/global';
import { LogAnalyserType, LogAnalyserStatusType } from '@/types';
import { ElNotification } from 'element-plus'
import { computed, ref } from 'vue';
import { storeToRefs } from 'pinia'
import { useClientLogStore } from '@/store/clientLog';


export const useClientLogAnalyser = () => {
  const store = useGlobalStore()
  const { setLogAnalyserStatus, getLogAnalyserStatus } = store
  const { logAnalyserStatusMap } = storeToRefs(store)
  const clientLogAnalyserStatus = computed(() => logAnalyserStatusMap.value[LogAnalyserType.Client])

  const clientStore = useClientLogStore();
  const {
    setFetchStatisticList,
    setAccountsFetchMap
  } = clientStore;

  const initClientLogAnalyser = async (file: File) => {
    setLogAnalyserStatus(LogAnalyserType.Client, LogAnalyserStatusType.None)
    try {
      const formData = new FormData();
      formData.append('file', file);
      setLogAnalyserStatus(LogAnalyserType.Client, LogAnalyserStatusType.Running)
      const res = await clientLogApi.uploadClientLog(formData)
      if (res.code === 0) {
        ElNotification.success({
          title: '提示',
          message: '客户端全量日志已上传并解析成功',
        })
        setLogAnalyserStatus(LogAnalyserType.Client, LogAnalyserStatusType.Ready)
      } else {
        setLogAnalyserStatus(LogAnalyserType.Client, LogAnalyserStatusType.Error)
        throw new Error(res.message)
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
      return;
    }
    try {
      const res = await clientLogApi.getAccountsQuery()
      setAccountsFetchMap(res.data)
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const getStatisticData = async () => {
    if (getLogAnalyserStatus(LogAnalyserType.Client) === LogAnalyserStatusType.None) {
      ElNotification.error({
        title: 'Error',
        message: '全量日志未解析完成',
      })
      return;
    }
    try {
      const res = await clientLogApi.getFetchStatistic()
      setFetchStatisticList(res.data)
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  return {
    clientLogAnalyserStatus,
    initClientLogAnalyser,
    getAccountsLogs,
    getStatisticData
  }
}

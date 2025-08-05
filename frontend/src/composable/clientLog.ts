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
    setAccountsFetchMap,
    setFundFetchMap,
    setPositionFetchMap,
    setOrderFetchMap,
    setOrderSummary,
    setTradeSummary,
    setTradeFetchMap,
    setIpoFetchMap,
    setIpoLotteryFetchMap,
    setFinableSecurityMap,
    setFinableSecurityFailed,
    setBasketSummary,
    setBasketOrderDetail,
    setBasketQueryData,
    setAlgorithmQueryData,
    setNewAlgorithmOrder,
    setConditionSummary,
    setConditionQueryData
  } = clientStore;

  const initClientLogAnalyser = async (files: File[]) => {
    setLogAnalyserStatus(LogAnalyserType.Client, LogAnalyserStatusType.None)
    try {
      setLogAnalyserStatus(LogAnalyserType.Client, LogAnalyserStatusType.Running)
      const res = await clientLogApi.uploadClientLog(files)
      if (res.code === 0) {
        ElNotification.success({
          title: '提示',
          message: `客户端全量日志已上传并解析成功，共上传 ${files.length} 个文件`,
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

  const filterLogList = async (content?: string) => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.filterLogList(content)
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

  const getAccountsLogs = async () => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getAccountsQuery()
      if (res.code === 0) {
        setAccountsFetchMap(res.data)
        return res.data
      } else {
        throw new Error(res.message)
      }
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const getStatisticData = async () => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getFetchStatistic()
      if (res.code !== 0) {
        throw new Error(res.message)
      }
      setFetchStatisticList(res.data)
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const getFundLogs = async () => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getFundQuery();
      if (res.code !== 0) {
        throw new Error(res.message)
      }
      setFundFetchMap(res.data)
      console.log(res.data)
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const getPositionLogs = async () => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getPositionQuery()
      if (res.code !== 0) {
        throw new Error(res.message)
      }
      setPositionFetchMap(res.data)
      return res.data
    } catch (e: any) {
}
  }

  const getOrderLogs = async () => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getOrderQuery()
      if (res.code !== 0) {
        throw new Error(res.message)
      }
      console.log(res.data)
      setOrderFetchMap(res.data)
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const getOrderSummary = async () => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getOrderSummary()
      if (res.code !== 0) {
        throw new Error(res.message)
      }
      setOrderSummary(res.data)
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const getTradeLogs = async () => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getTradeQuery()
      if (res.code !== 0) {
        throw new Error(res.message)
      }
      setTradeFetchMap(res.data)
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const getTradeSummary = async () => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getTradeSummary()
      if (res.code !== 0) {
        throw new Error(res.message)
      }
      setTradeSummary(res.data)
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const getIpoLogs = async () => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getIpoQuery()
      if (res.code !== 0) {
        throw new Error(res.message)
      }
      setIpoFetchMap(res.data)
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const getIpoLotteryLogs = async () => {

    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getIpoLotteryQuery()
      if (res.code !== 0) {
        throw new Error(res.message)
      }
      setIpoLotteryFetchMap(res.data)
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const getFinableSecurityData = async () => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getFinableSecurityData()
      if (res.code !== 0) {
        throw new Error(res.message)
      }
      setFinableSecurityMap(res.data)
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const getFinableSecurityFailed = async () => {

    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getFinableSecurityFailed()
      if (res.code !== 0) {
        throw new Error(res.message)
      }
      setFinableSecurityFailed(res.data)
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const getBasketSummaryData = async (source: string, fund: string, stockcode: string) => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getBasketSummaryData(source, fund, stockcode)
      if (res.code !== 0) {
        throw new Error(res.message)
      }
      setBasketSummary(res.data)
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const getBasketInstanceDetail = async (instanceid: string) => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getBasketInstanceDetail(instanceid)
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

  const getBasketOrderDetail = async (instanceid: string) => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getBasketOrderDetail(instanceid)
      if (res.code !== 0) {
        throw new Error(res.message)
      }
      setBasketOrderDetail(res.data)
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const getBasketQueryData = async () => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getBasketQueryData()
      if (res.code !== 0) {
        throw new Error(res.message)
      }
      setBasketQueryData(res.data)
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const getBasketInitReqs = async () => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getBasketInitReqs()
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

  const getNewAlgorithmOrder = async () => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getNewAlgorithmOrder()
      if (res.code !== 0) {
        throw new Error(res.message)
      }
      setNewAlgorithmOrder(res.data)
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const getAlgorithmQueryData = async () => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getAlgorithmQueryData()
      if (res.code !== 0) {
        throw new Error(res.message)
      }
      setAlgorithmQueryData(res.data)
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const getAlgorithmDetail = async (instanceid: string) => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getAlgorithmDetail(instanceid)
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

  const getAlgorithmPushDetail = async (instanceid: string, push_type: string) => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getAlgorithmPushDetail(instanceid, push_type)
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

  const getAlgorithmCode = async () => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getAlgorithmCode()
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

  function checkoutClientLogAnalyserStatus () {
    // if (getLogAnalyserStatus(LogAnalyserType.Client) === LogAnalyserStatusType.None) {
    //   ElNotification.error({
    //     title: 'Error',
    //     message: '全量日志未解析完成',
    //   })
    //   return false;
    // }
    return true
  }

  const getConditionSummaryData = async () => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getConditionSummaryData()
      if (res.code !== 0) {
        throw new Error(res.message)
      }
      setConditionSummary(res.data)
      return res.data
    } catch (e: any) {
      ElNotification.error({
        title: 'Error',
        message: e.message,
      })
    }
  }

  const getConditionInstanceDetailData = async (order_no: string) => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getConditionInstanceDetailData(order_no)
      console.log(res, typeof res)
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

  const getConditionOrderDetailData = async (order_no: string) => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getConditionOrderDetailData(order_no)
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

  const getConditionSecurityOrderDetailData = async (order_no: string, fund: string, security: string) => {
    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getConditionSecurityOrderDetailData(order_no, fund, security)
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

  const getConditionInitReqsData = async (order_no: string) => {

    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getConditionInitReqsData(order_no)
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

  const getConditionQueryData = async (querytime: string) => {

    if (!checkoutClientLogAnalyserStatus()) {
      return;
    }
    try {
      const res = await clientLogApi.getConditionQueryData(querytime)
      if (res.code !== 0) {
        throw new Error(res.message)
      }
      setConditionQueryData(res.data)
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
    filterLogList,
    getAccountsLogs,
    getStatisticData,
    getFundLogs,
    getPositionLogs,
    getOrderLogs,
    getOrderSummary,
    getTradeLogs,
    getTradeSummary,
    getIpoLogs,
    getIpoLotteryLogs,
    getFinableSecurityData,
    getFinableSecurityFailed,
    getBasketSummaryData,
    getBasketInstanceDetail,
    getBasketOrderDetail,
    getBasketQueryData,
    getBasketInitReqs,
    getNewAlgorithmOrder,
    getAlgorithmQueryData,
    getAlgorithmDetail,
    getAlgorithmPushDetail,
    getAlgorithmCode,
    getConditionSummaryData,
    getConditionInstanceDetailData,
    getConditionOrderDetailData,
    getConditionSecurityOrderDetailData,
    getConditionInitReqsData,
    getConditionQueryData
  }
}

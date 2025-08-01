import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useClientLogStore = defineStore('clientLog', () => {
  const fetchStatisticList = ref<any[]>([])
  const setFetchStatisticList = (data: any[]) => {
    fetchStatisticList.value = data
  }

  const accountsFetchMap = ref<any>({});
  const setAccountsFetchMap = (data: any) => {
    accountsFetchMap.value = data
  }

  const fundFetchMap = ref<any>({});
  const setFundFetchMap = (data: any) => {
    fundFetchMap.value = data
  }

  const positionFetchMap = ref<any>({});
  const setPositionFetchMap = (data: any) => {
    positionFetchMap.value = data
  }

  const orderFetchMap = ref<any>({});
  const setOrderFetchMap = (data: any) => {
    orderFetchMap.value = data
  }

  const orderSummary = ref<any>({});
  const setOrderSummary = (data: any) => {
    orderSummary.value = data
  }

  const tradeFetchMap = ref<any>({});
  const setTradeFetchMap = (data: any) => {
    tradeFetchMap.value = data
  }

  const tradeSummary = ref<any>({});
  const setTradeSummary = (data: any) => {
    tradeSummary.value = data
  }

  const ipoFetchMap = ref<any>([]);
  const setIpoFetchMap = (data: any) => {
    ipoFetchMap.value = data
  }

  const ipoLotteryFetchMap = ref<any>([]);
  const setIpoLotteryFetchMap = (data: any) => {
    ipoLotteryFetchMap.value = data
  }

  const finableSecurityMap = ref<any>({});
  const setFinableSecurityMap = (data: any) => {
    finableSecurityMap.value = data
  }

  const finableSecurityFailed = ref<any>([]);
  const setFinableSecurityFailed = (data: any) => {
    finableSecurityFailed.value = data
  }

  const basketSummary = ref<any>([]);
  const setBasketSummary = (data: any) => {
    basketSummary.value = data
  }

  const basketOrderDetail = ref<any>([]);
  const setBasketOrderDetail = (data: any) => {
    basketOrderDetail.value = data
  }

  const basketQueryData = ref<any>({});
  const setBasketQueryData = (data: any) => {
    basketQueryData.value = data
  }

  const newAlgorithmOrder = ref<any>([]);
  const setNewAlgorithmOrder = (data: any) => {
    newAlgorithmOrder.value = data
  }

  const algorithmQueryData = ref<any>({});
  const setAlgorithmQueryData = (data: any) => {
    algorithmQueryData.value = data
  }

  const conditionSummary = ref<any>({});
  const setConditionSummary = (data: any) => {
    conditionSummary.value = data
  }

  const conditionQueryData = ref<any>({});
  const setConditionQueryData = (data: any) => {
    conditionQueryData.value = data
  }

  return {
    fetchStatisticList,
    setFetchStatisticList,
    accountsFetchMap,
    setAccountsFetchMap,
    fundFetchMap,
    setFundFetchMap,
    positionFetchMap,
    setPositionFetchMap,
    orderFetchMap,
    setOrderFetchMap,
    orderSummary,
    setOrderSummary,
    tradeFetchMap,
    setTradeFetchMap,
    tradeSummary,
    setTradeSummary,
    ipoFetchMap,
    setIpoFetchMap,
    ipoLotteryFetchMap,
    setIpoLotteryFetchMap,
    finableSecurityMap,
    setFinableSecurityMap,
    finableSecurityFailed,
    setFinableSecurityFailed,
    basketSummary,
    setBasketSummary,
    basketOrderDetail,
    setBasketOrderDetail,
    basketQueryData,
    setBasketQueryData,
    algorithmQueryData,
    setAlgorithmQueryData,
    newAlgorithmOrder,
    setNewAlgorithmOrder,
    conditionSummary,
    setConditionSummary,
    conditionQueryData,
    setConditionQueryData
  }
})

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

  const ipoFetchMap = ref<any>({});
  const setIpoFetchMap = (data: any) => {
    ipoFetchMap.value = data
  }

  const ipoLotteryFetchMap = ref<any>({});
  const setIpoLotteryFetchMap = (data: any) => {
    ipoLotteryFetchMap.value = data
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
  }
})

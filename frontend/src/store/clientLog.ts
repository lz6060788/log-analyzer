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
  }
})

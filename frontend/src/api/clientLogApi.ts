import type { RespType } from '@/types/res';
import apiClient from './axios';
import type { AxiosResponse } from 'axios';

const api = {
  uploadClientLog: (formData: FormData): Promise<RespType<null>> => {
    return apiClient.post('/log/client/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  getAccountsQuery: (): Promise<RespType<any[]>> => {
    return apiClient.get('/log/client/query_accounts_logs');
  },
  getFetchStatistic: (): Promise<RespType<any[]>> => {
    return apiClient.get('/log/client/query_fetch_statistics');
  },
  getFundQuery: (): Promise<RespType<any>> => {
    return apiClient.get('/log/client/query_fund_logs');
  },
  getPositionQuery: (): Promise<RespType<any>> => {
    return apiClient.get('/log/client/query_position_logs');
  },
  getOrderQuery: (): Promise<RespType<any>> => {
    return apiClient.get('/log/client/query_order_logs');
  },
  getOrderSummary: (): Promise<RespType<any>> => {
    return apiClient.get(`/log/client/query_order_summary`);
  },
  getTradeQuery: (): Promise<RespType<any>> => {
    return apiClient.get(`/log/client/trade_query_data`);
  },
  getTradeSummary: (): Promise<RespType<any>> => {
    return apiClient.get(`/log/client/query_trade_summary`);
  },
  getIpoQuery: (): Promise<RespType<any>> => {
    return apiClient.get(`/log/client/ipo_query_data`);
  },
  getIpoLotteryQuery: (): Promise<RespType<any>> => {
    return apiClient.get(`/log/client/ipo_lottery_data`);
  },
};

export default api;

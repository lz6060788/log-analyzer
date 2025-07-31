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
  getFinableSecurityData: (): Promise<RespType<any>> => {
    return apiClient.get(`/log/client/finable_security_data`);
  },
  getFinableSecurityFailed: (): Promise<RespType<any>> => {
    return apiClient.get(`/log/client/finable_security_failed`);
  },
  getBasketSummaryData: (source: string, fund: string, stockcode: string): Promise<RespType<any>> => {
    return apiClient.get(`/log/client/basket_summary_data`, {
      params: {
        source,
        fund,
        stockcode
      }
    });
  },
  getBasketInstanceDetail: (instanceid: string): Promise<RespType<any>> => {
    return apiClient.get(`/log/client/basket_instance_detail`, {
      params: {
        instanceid
      }
    });
  },
  getBasketOrderDetail: (instanceid: string): Promise<RespType<any>> => {
    return apiClient.get(`/log/client/basket_order_detail`, {
      params: {
        instanceid
      }
    });
  },
  getBasketQueryData: (): Promise<RespType<any>> => {
    return apiClient.get(`/log/client/basket_query_data`);
  },
  getBasketInitReqs: (): Promise<RespType<any>> => {
    return apiClient.get(`/log/client/basket_initreqs`);
  },
  getNewAlgorithmOrder: (): Promise<RespType<any>> => {
    return apiClient.get(`/log/client/get_new_algorithm_order`);
  },
  getAlgorithmQueryData: (): Promise<RespType<any>> => {
    return apiClient.get(`/log/client/algorithm_query_data`);
  },
  getAlgorithmDetail: (instanceid: string): Promise<RespType<any>> => {
    return apiClient.get(`/log/client/algorithm_detail`, {
      params: {
        instanceid
      }
    });
  },
  getAlgorithmPushDetail: (instanceid: string, push_type: string): Promise<RespType<any>> => {
    return apiClient.get(`/log/client/algorithm_push_detail`, {
      params: {
        instanceid,
        push_type
      }
    });
  },
  getAlgorithmCode: (): Promise<RespType<any>> => {
    return apiClient.get(`/log/client/algorithm_code`);
  }
};

export default api;

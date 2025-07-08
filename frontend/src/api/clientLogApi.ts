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
  getFundQuery: (): Promise<RespType<any[]>> => {
    return apiClient.get('/log/client/query_fund_logs');
  },
};

export default api;

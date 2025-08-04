import type { RespType } from '@/types/res';
import apiClient from './axios';
import type { OperationLogLine } from '@/types/operation/log';

const api = {
  uploadOperationLog: (files: File[]): Promise<RespType<null>> => {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    return apiClient.post('/log/operation/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  filterLogList: (content: string): Promise<RespType<OperationLogLine[]>> => {
    return apiClient.get('/log/operation/filter_log_list', {
      params: {
        content
      }
    });
  },
};

export default api;

import type { RespType } from '@/types/res';
import apiClient from './axios';

const api = {
    /**
     * 获取服务状态
     * @returns 服务状态
     */
    getStatus: (): Promise<RespType<{client_status: boolean, operation_status: boolean}>> => {
        return apiClient.get('/log/status');
    }
};

export default api;

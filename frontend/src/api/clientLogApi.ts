import apiClient from './axios';

const api = {
  uploadClientLog: (formData: FormData) => {
    return apiClient.post('/log/client/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  getAccountsQuery: () => {
    return apiClient.get('/log/client/query_accounts_logs');
  }
};

export default api;

import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api', // 从环境变量获取基础URL
  timeout: 30 * 1000, // 超时时间
});

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    // 在这里可以添加token等信息
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  response => {
    return response.data;
  },
  error => {
    // 处理网络错误等
    return Promise.reject(error);
  }
);

export default apiClient;

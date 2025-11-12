import axios from 'axios';

// 根据环境变量设置基础URL
const getBaseURL = () => {
  if (import.meta.env.DEV) {
    return '/api'; // 开发环境
  } else {
    return '/'; // 生产环境
  }
};

const apiClient = axios.create({
  baseURL: getBaseURL(),
  timeout: 30 * 1000, // 超时时间
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
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

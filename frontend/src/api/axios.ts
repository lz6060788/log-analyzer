import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api', // 从环境变量获取基础URL
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
    console.log('Axios响应拦截器 - 原始响应:', response);
    console.log('Axios响应拦截器 - response.data类型:', typeof response.data);
    console.log('Axios响应拦截器 - response.data内容:', response.data);
    console.log('Axios响应拦截器 - Content-Type:', response.headers['content-type']);
    return response.data;
  },
  error => {
    // 处理网络错误等
    return Promise.reject(error);
  }
);

export default apiClient;

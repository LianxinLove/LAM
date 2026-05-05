/**
 * API 基础配置模块
 *
 * 认证方式：Session-Cookie
 * 1. 创建 axios 实例，配置基础 URL 和超时时间
 * 2. 启用 withCredentials：自动发送和接收 Cookie
 * 3. 响应拦截器：统一处理 401 未授权错误，自动跳转登录页
 *
 * 技术要点：
 * - 使用 axios.create() 创建独立实例
 * - withCredentials: true 允许跨域请求携带 Cookie
 * - Session ID 存储在 Cookie 中，浏览器自动管理
 * - 401 错误自动跳转登录页（避免已在登录页时重复跳转）
 */

import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';

// 从环境变量获取 API 基础地址
// 使用相对路径 '/api'，配合 Nginx 反向代理，可在任意域名下工作
const API_BASE_URL = (import.meta as any).env.VITE_API_BASE_URL || '/api';

/**
 * Axios 实例
 *
 * 配置说明：
 * - baseURL: API 基础路径
 * - timeout: 请求超时时间（毫秒），10秒
 * - withCredentials: 允许跨域请求携带 Cookie（关键配置）
 */
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,  // 增加超时时间以支持文件上传
  withCredentials: true,  // 允许跨域携带 Cookie，Session-Cookie 认证的关键配置
});

/**
 * 请求拦截器
 *
 * 功能：在请求发出前进行处理
 *
 * 技术要点：
 * - Session-Cookie 认证方式不需要手动添加 token
 * - 浏览器会自动携带 Cookie 中的 session_id
 * - FormData 时不设置 Content-Type，让浏览器自动设置
 */
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 如果 data 是 FormData，不设置 Content-Type
    // 让浏览器自动设置并添加 boundary 参数
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    } else if (!config.headers['Content-Type']) {
      config.headers['Content-Type'] = 'application/json';
    }
    return config;
  },
  (error) => {
    // 请求配置错误处理
    return Promise.reject(error);
  }
);

/**
 * 响应拦截器
 *
 * 功能：统一处理响应数据和错误
 *
 * 技术要点：
 * - 成功响应：直接返回 response.data，简化后续调用
 * - 401 错误：Session 过期或未登录，跳转到登录页
 * - 防止无限循环：已在登录页时不跳转
 * - 其他错误：返回后端返回的错误数据
 */
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // 成功响应直接返回 data 部分，简化调用方使用
    return response.data;
  },
  (error) => {
    if (error.response) {
      // 处理 HTTP 错误响应
      const { status } = error.response;

      // 401 Unauthorized: Session 过期或未登录
      if (status === 401) {
        // 检查当前是否已经在登录页，避免无限循环
        if (!window.location.pathname.startsWith('/login')) {
          // Session 过期，跳转到登录页
          // Cookie 中的 session_id 会在浏览器端自动过期清理
          window.location.href = '/login';
        }
      }

      // 返回后端错误数据，包含 message 和 error_code 等信息
      return Promise.reject(error.response.data);
    }

    // 网络错误或请求未发出
    return Promise.reject(error);
  }
);

export default api;

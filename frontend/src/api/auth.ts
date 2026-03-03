/**
 * 认证相关 API 接口
 *
 * 认证方式：Session-Cookie
 *
 * 功能模块：
 * - 用户注册
 * - 用户登录
 * - 获取当前用户信息
 * - 用户登出
 *
 * 技术要点：
 * - Session ID 存储在 Cookie 中，由浏览器自动管理
 * - axios 已配置 withCredentials: true，自动携带 Cookie
 * - 登录成功后，后端创建 Session 并通过 Cookie 返回 session_id
 * - 登出需要调用后端 API 清除服务端 Session
 */

import api from './index';
import type { LoginRequest, RegisterRequest, AuthResponse, ApiResponse } from '../types';

/**
 * 用户注册
 *
 * @param data - 注册信息（用户名、密码、邮箱）
 * @returns 包含用户信息的响应
 *
 * 技术要点：
 * - 注册成功后自动登录，后端创建 Session
 * - Session ID 通过 Set-Cookie header 返回，浏览器自动存储
 * - 前端不需要手动存储 token
 */
export const register = (data: RegisterRequest): Promise<ApiResponse<AuthResponse>> => {
  return api.post('/auth/register', data);
};

/**
 * 用户登录
 *
 * @param data - 登录信息（用户名、密码）
 * @returns 包含用户信息的响应
 *
 * 技术要点：
 * - 登录成功后，后端创建 Session
 * - Session ID 通过 Set-Cookie header 返回
 * - 后续请求浏览器会自动携带 Cookie
 *
 * 登录成功后：
 * - 将用户信息存储到 AuthContext 中
 * - 不需要存储 token，由 Cookie 管理
 */
export const login = (data: LoginRequest): Promise<ApiResponse<AuthResponse>> => {
  return api.post('/auth/login', data);
};

/**
 * 获取当前用户信息
 *
 * @returns 当前用户的详细信息
 *
 * 技术要点：
 * - 通过 Cookie 中的 Session ID 验证身份
 * - 用于刷新页面后恢复用户登录状态
 * - 验证 Session 是否仍然有效
 */
export const getCurrentUser = (): Promise<ApiResponse<any>> => {
  return api.get('/auth/me');
};

/**
 * 用户登出
 *
 * 技术要点：
 * - 调用后端 API 清除服务端 Session
 * - Cookie 中的 session_id 会被标记为过期
 * - 浏览器会自动清理过期的 Cookie
 *
 * 注意：登出后应调用 AuthContext 的 logout 方法更新应用状态
 */
export const logout = (): Promise<ApiResponse<void>> => {
  return api.post('/auth/logout');
};

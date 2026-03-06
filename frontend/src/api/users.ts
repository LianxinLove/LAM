/**
 * 用户管理 API 接口
 */

import api from './index';
import type { ApiResponse } from '../types';

export interface User {
  id: number;
  username: string;
  email?: string;
  is_superuser: boolean;
  is_active: boolean;
  created_at?: string;
}

export interface UserSimple {
  id: number;
  username: string;
  email?: string;
}

/**
 * 获取用户列表
 */
export const getUsers = (params?: {
  search?: string;
  is_active?: boolean;
  page?: number;
  page_size?: number;
}): Promise<ApiResponse<{ items: User[]; total: number }>> => {
  return api.get('/users', { params });
};

/**
 * 获取用户简单列表（用于下拉选择）
 */
export const getUsersSimple = (params?: {
  is_active?: boolean;
}): Promise<ApiResponse<UserSimple[]>> => {
  return api.get('/users/simple', { params });
};

/**
 * 获取用户详情
 */
export const getUser = (id: number): Promise<ApiResponse<User>> => {
  return api.get(`/users/${id}`);
};

/**
 * 更新用户信息
 */
export const updateUser = (
  id: number,
  data: Partial<User>
): Promise<ApiResponse<User>> => {
  return api.put(`/users/${id}`, data);
};

/**
 * 删除用户
 */
export const deleteUser = (id: number): Promise<ApiResponse<void>> => {
  return api.delete(`/users/${id}`);
};

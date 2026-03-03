/**
 * 资产类别 API 接口
 *
 * 功能模块：
 * - 获取类别列表（支持分页）
 * - 获取类别详情
 * - 创建类别
 * - 更新类别
 * - 删除类别
 *
 * 数据结构：
 * - 支持树形结构（通过 parent_id 关联父类别）
 * - 类别名称唯一
 */

import api from './index';
import type { Category, ApiResponse, PaginatedResponse, QueryParams } from '../types';

/**
 * 类别表单数据类型
 */
export interface CategoryFormData {
  name: string;           // 类别名称（必填）
  parent_id?: number;     // 父类别 ID（可选，用于构建层级结构）
}

/**
 * 获取类别列表
 *
 * @param params - 查询参数（分页）
 * @returns 分页的类别列表
 */
export const getCategories = (params?: QueryParams): Promise<ApiResponse<PaginatedResponse<Category>>> => {
  return api.get('/categories', { params });
};

/**
 * 获取类别详情
 *
 * @param id - 类别 ID
 * @returns 类别详细信息
 */
export const getCategory = (id: number): Promise<ApiResponse<Category>> => {
  return api.get(`/categories/${id}`);
};

/**
 * 创建类别
 *
 * @param data - 类别信息
 * @returns 创建的类别信息
 */
export const createCategory = (data: CategoryFormData): Promise<ApiResponse<Category>> => {
  return api.post('/categories', data);
};

/**
 * 更新类别
 *
 * @param id - 类别 ID
 * @param data - 更新的类别信息
 * @returns 更新后的类别信息
 */
export const updateCategory = (id: number, data: CategoryFormData): Promise<ApiResponse<Category>> => {
  return api.put(`/categories/${id}`, data);
};

/**
 * 删除类别
 *
 * @param id - 类别 ID
 * @returns 空
 *
 * 注意：如果类别下有关联的资产或耗材，可能无法删除
 */
export const deleteCategory = (id: number): Promise<ApiResponse<void>> => {
  return api.delete(`/categories/${id}`);
};

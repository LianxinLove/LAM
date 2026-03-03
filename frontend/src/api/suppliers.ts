/**
 * 供应商管理 API 接口
 *
 * 功能模块：
 * - 获取供应商列表（支持分页）
 * - 获取供应商详情
 * - 创建供应商
 * - 更新供应商
 * - 删除供应商
 */

import api from './index';
import type { Supplier, ApiResponse, PaginatedResponse, QueryParams } from '../types';

/**
 * 供应商表单数据类型
 */
export interface SupplierFormData {
  name: string;           // 供应商名称（必填）
  contact?: string;       // 联系人
  phone?: string;         // 联系电话
  email?: string;         // 电子邮箱
  address?: string;       // 地址
}

/**
 * 获取供应商列表
 *
 * @param params - 查询参数（分页）
 * @returns 分页的供应商列表
 */
export const getSuppliers = (params?: QueryParams): Promise<ApiResponse<PaginatedResponse<Supplier>>> => {
  return api.get('/suppliers', { params });
};

/**
 * 获取供应商详情
 *
 * @param id - 供应商 ID
 * @returns 供应商详细信息
 */
export const getSupplier = (id: number): Promise<ApiResponse<Supplier>> => {
  return api.get(`/suppliers/${id}`);
};

/**
 * 创建供应商
 *
 * @param data - 供应商信息
 * @returns 创建的供应商信息
 */
export const createSupplier = (data: SupplierFormData): Promise<ApiResponse<Supplier>> => {
  return api.post('/suppliers', data);
};

/**
 * 更新供应商
 *
 * @param id - 供应商 ID
 * @param data - 更新的供应商信息
 * @returns 更新后的供应商信息
 */
export const updateSupplier = (id: number, data: SupplierFormData): Promise<ApiResponse<Supplier>> => {
  return api.put(`/suppliers/${id}`, data);
};

/**
 * 删除供应商
 *
 * @param id - 供应商 ID
 * @returns 空
 */
export const deleteSupplier = (id: number): Promise<ApiResponse<void>> => {
  return api.delete(`/suppliers/${id}`);
};

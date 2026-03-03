/**
 * 资产管理 API 接口
 *
 * 功能模块：
 * - 获取资产列表（支持分页、筛选）
 * - 获取资产详情
 * - 创建资产
 * - 更新资产
 * - 删除资产
 *
 * 筛选参数（QueryParams）：
 * - category_id: 按类别筛选
 * - status: 按状态筛选（available/in_use/maintenance/retired）
 * - page: 页码
 * - page_size: 每页数量
 */

import api from './index';
import type { Asset, AssetFormData, ApiResponse, PaginatedResponse, QueryParams } from '../types';

/**
 * 获取资产列表
 *
 * @param params - 查询参数（分页、筛选）
 * @returns 分页的资产列表
 *
 * 使用示例：
 * ```ts
 * // 获取所有资产
 * const assets = await getAssets();
 *
 * // 按类别筛选
 * const electronics = await getAssets({ category_id: 1 });
 *
 * // 按状态筛选
 * const available = await getAssets({ status: 'available' });
 * ```
 */
export const getAssets = (params?: QueryParams): Promise<ApiResponse<PaginatedResponse<Asset>>> => {
  return api.get('/assets', { params });
};

/**
 * 获取资产详情
 *
 * @param id - 资产 ID
 * @returns 资产详细信息
 */
export const getAsset = (id: number): Promise<ApiResponse<Asset>> => {
  return api.get(`/assets/${id}`);
};

/**
 * 创建资产
 *
 * @param data - 资产信息
 * @returns 创建的资产信息
 *
 * 必填字段：name, code, category_id
 * 可选字段：supplier_id, specifications, purchase_date, purchase_price, location, custodian, remarks
 */
export const createAsset = (data: AssetFormData): Promise<ApiResponse<Asset>> => {
  return api.post('/assets', data);
};

/**
 * 更新资产
 *
 * @param id - 资产 ID
 * @param data - 更新的资产信息
 * @returns 更新后的资产信息
 */
export const updateAsset = (id: number, data: AssetFormData): Promise<ApiResponse<Asset>> => {
  return api.put(`/assets/${id}`, data);
};

/**
 * 删除资产
 *
 * @param id - 资产 ID
 * @returns 空
 *
 * 注意：删除操作不可恢复，请谨慎使用
 */
export const deleteAsset = (id: number): Promise<ApiResponse<void>> => {
  return api.delete(`/assets/${id}`);
};

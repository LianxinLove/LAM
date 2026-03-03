/**
 * 耗材管理 API 接口
 *
 * 功能模块：
 * - 获取耗材列表（支持分页、筛选）
 * - 获取耗材详情
 * - 创建耗材
 * - 更新耗材
 * - 删除耗材
 *
 * 筛选参数（QueryParams）：
 * - category_id: 按类别筛选
 * - low_stock: 是否仅显示低库存项目（布尔值）
 * - page: 页码
 * - page_size: 每页数量
 */

import api from './index';
import type { Consumable, ConsumableFormData, ApiResponse, PaginatedResponse, QueryParams } from '../types';

/**
 * 获取耗材列表
 *
 * @param params - 查询参数（分页、筛选）
 * @returns 分页的耗材列表
 *
 * 使用示例：
 * ```ts
 * // 获取所有耗材
 * const consumables = await getConsumables();
 *
 * // 仅获取低库存耗材
 * const lowStock = await getConsumables({ low_stock: true });
 * ```
 */
export const getConsumables = (params?: QueryParams): Promise<ApiResponse<PaginatedResponse<Consumable>>> => {
  return api.get('/consumables', { params });
};

/**
 * 获取耗材详情
 *
 * @param id - 耗材 ID
 * @returns 耗材详细信息
 */
export const getConsumable = (id: number): Promise<ApiResponse<Consumable>> => {
  return api.get(`/consumables/${id}`);
};

/**
 * 创建耗材
 *
 * @param data - 耗材信息
 * @returns 创建的耗材信息
 *
 * 必填字段：name, category_id, unit, stock, min_stock
 * 可选字段：supplier_id, price, location
 */
export const createConsumable = (data: ConsumableFormData): Promise<ApiResponse<Consumable>> => {
  return api.post('/consumables', data);
};

/**
 * 更新耗材
 *
 * @param id - 耗材 ID
 * @param data - 更新的耗材信息
 * @returns 更新后的耗材信息
 */
export const updateConsumable = (id: number, data: ConsumableFormData): Promise<ApiResponse<Consumable>> => {
  return api.put(`/consumables/${id}`, data);
};

/**
 * 删除耗材
 *
 * @param id - 耗材 ID
 * @returns 空
 */
export const deleteConsumable = (id: number): Promise<ApiResponse<void>> => {
  return api.delete(`/consumables/${id}`);
};

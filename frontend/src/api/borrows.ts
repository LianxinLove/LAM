/**
 * 资产借用 API 接口
 *
 * 功能模块：
 * - 获取借用记录列表（支持分页、筛选）
 * - 获取借用记录详情
 * - 创建借用记录（借用资产）
 * - 归还资产
 * - 删除借用记录
 *
 * 筛选参数（QueryParams）：
 * - status: 按状态筛选（borrowed/returned）
 * - borrower_id: 按借用人筛选
 * - my: 是否仅查看当前用户的记录（布尔值）
 */

import api from './index';
import type { BorrowRecord, BorrowFormData, ApiResponse, PaginatedResponse, QueryParams } from '../types';

/**
 * 获取借用记录列表
 *
 * @param params - 查询参数（分页、筛选）
 * @returns 分页的借用记录列表
 *
 * 使用示例：
 * ```ts
 * // 获取当前用户的借用记录
 * const myBorrows = await getBorrows({ my: true });
 *
 * // 获取所有借用中的记录
 * const borrowed = await getBorrows({ status: 'borrowed' });
 * ```
 */
export const getBorrows = (params?: QueryParams): Promise<ApiResponse<PaginatedResponse<BorrowRecord>>> => {
  return api.get('/borrows', { params });
};

/**
 * 获取借用记录详情
 *
 * @param id - 借用记录 ID
 * @returns 借用记录详细信息
 */
export const getBorrow = (id: number): Promise<ApiResponse<BorrowRecord>> => {
  return api.get(`/borrows/${id}`);
};

/**
 * 创建借用记录（借用资产）
 *
 * @param data - 借用信息
 * @returns 创建的借用记录信息
 *
 * 必填字段：asset_id
 * 可选字段：purpose（用途说明）
 *
 * 业务规则：
 * - 只能借用状态为 available（可用）的资产
 * - 借用成功后，资产状态自动变为 in_use（使用中）
 */
export const createBorrow = (data: BorrowFormData): Promise<ApiResponse<BorrowRecord>> => {
  return api.post('/borrows', data);
};

/**
 * 归还资产
 *
 * @param id - 借用记录 ID
 * @returns 更新后的借用记录信息
 *
 * 业务规则：
 * - 只能归还自己的借用记录
 * - 归还成功后，资产状态自动变为 available（可用）
 * - 记录归还时间和状态变更
 */
export const returnAsset = (id: number): Promise<ApiResponse<BorrowRecord>> => {
  return api.post(`/borrows/${id}/return`);
};

/**
 * 删除借用记录
 *
 * @param id - 借用记录 ID
 * @returns 空
 *
 * 注意：删除操作通常仅用于清理历史数据，正常业务流程不需要删除
 */
export const deleteBorrow = (id: number): Promise<ApiResponse<void>> => {
  return api.delete(`/borrows/${id}`);
};

/**
 * 耗材领用 API 接口
 *
 * 功能模块：
 * - 获取领用记录列表（支持分页、筛选）
 * - 获取领用记录详情
 * - 创建领用申请
 * - 审批领用申请（批准/拒绝）
 * - 删除领用记录
 *
 * 筛选参数（QueryParams）：
 * - status: 按状态筛选（pending/approved/rejected）
 * - applicant_id: 按申请人筛选
 * - my: 是否仅查看当前用户的申请（布尔值）
 *
 * 工作流程：
 * 1. 用户提交领用申请（status: pending）
 * 2. 管理员审批（status: approved/rejected）
 * 3. 审批通过后自动扣减库存
 */

import api from './index';
import type { PickRecord, PickFormData, ApiResponse, PaginatedResponse, QueryParams } from '../types';

/**
 * 获取领用记录列表
 *
 * @param params - 查询参数（分页、筛选）
 * @returns 分页的领用记录列表
 *
 * 使用示例：
 * ```ts
 * // 获取我的领用申请
 * const myPicks = await getPicks({ my: true });
 *
 * // 获取待审批的申请（管理员）
 * const pending = await getPicks({ status: 'pending' });
 * ```
 */
export const getPicks = (params?: QueryParams): Promise<ApiResponse<PaginatedResponse<PickRecord>>> => {
  return api.get('/picks', { params });
};

/**
 * 获取领用记录详情
 *
 * @param id - 领用记录 ID
 * @returns 领用记录详细信息
 */
export const getPick = (id: number): Promise<ApiResponse<PickRecord>> => {
  return api.get(`/picks/${id}`);
};

/**
 * 创建领用申请
 *
 * @param data - 领用申请信息
 * @returns 创建的领用申请信息
 *
 * 必填字段：item_id, quantity
 * 可选字段：purpose（用途说明）
 *
 * 业务规则：
 * - 申请时不立即扣减库存
 * - 审批通过后才扣减库存
 */
export const createPick = (data: PickFormData): Promise<ApiResponse<PickRecord>> => {
  return api.post('/picks', data);
};

/**
 * 批准领用申请
 *
 * @param id - 领用申请 ID
 * @returns 更新后的领用申请信息
 *
 * 权限：仅管理员可操作
 * 效果：状态变更为 approved，自动扣减耗材库存
 */
export const approvePick = (id: number): Promise<ApiResponse<PickRecord>> => {
  return api.post(`/picks/${id}/approve`, { action: 'approve' });
};

/**
 * 拒绝领用申请
 *
 * @param id - 领用申请 ID
 * @param reason - 拒绝原因（可选）
 * @returns 更新后的领用申请信息
 *
 * 权限：仅管理员可操作
 * 效果：状态变更为 rejected，不扣减库存
 */
export const rejectPick = (id: number, reason?: string): Promise<ApiResponse<PickRecord>> => {
  return api.post(`/picks/${id}/approve`, { action: 'reject', reason });
};

/**
 * 删除领用记录
 *
 * @param id - 领用记录 ID
 * @returns 空
 *
 * 注意：通常只能删除待审批状态的申请
 */
export const deletePick = (id: number): Promise<ApiResponse<void>> => {
  return api.delete(`/picks/${id}`);
};

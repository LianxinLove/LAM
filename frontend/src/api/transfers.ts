/**
 * 资产调拨 API 接口
 *
 * 功能模块：
 * - 获取调拨申请列表（支持分页、筛选）
 * - 获取调拨申请详情
 * - 创建调拨申请
 * - 审批调拨申请（批准/拒绝）
 * - 删除调拨记录
 *
 * 筛选参数（QueryParams）：
 * - status: 按状态筛选（pending/approved/rejected）
 * - applicant_id: 按申请人筛选
 *
 * 工作流程：
 * 1. 用户提交调拨申请（status: pending）
 * 2. 管理员审批（status: approved/rejected）
 * 3. 审批通过后更新资产位置信息
 *
 * 权限：仅管理员可使用此功能
 */

import api from './index';
import type { TransferRequest, TransferFormData, ApiResponse, PaginatedResponse, QueryParams } from '../types';

/**
 * 获取调拨申请列表
 *
 * @param params - 查询参数（分页、筛选）
 * @returns 分页的调拨申请列表
 *
 * 使用示例：
 * ```ts
 * // 获取待审批的调拨申请
 * const pending = await getTransfers({ status: 'pending' });
 * ```
 */
export const getTransfers = (params?: QueryParams): Promise<ApiResponse<PaginatedResponse<TransferRequest>>> => {
  return api.get('/transfers', { params });
};

/**
 * 获取调拨申请详情
 *
 * @param id - 调拨申请 ID
 * @returns 调拨申请详细信息
 */
export const getTransfer = (id: number): Promise<ApiResponse<TransferRequest>> => {
  return api.get(`/transfers/${id}`);
};

/**
 * 创建调拨申请
 *
 * @param data - 调拨申请信息
 * @returns 创建的调拨申请信息
 *
 * 必填字段：asset_id, to_location, reason
 *
 * 业务规则：
 * - from_location 自动从资产的当前 location 获取
 * - 审批通过后更新资产的 location
 */
export const createTransfer = (data: TransferFormData): Promise<ApiResponse<TransferRequest>> => {
  return api.post('/transfers', data);
};

/**
 * 批准调拨申请
 *
 * @param id - 调拨申请 ID
 * @returns 更新后的调拨申请信息
 *
 * 权限：仅管理员可操作
 * 效果：状态变更为 approved，更新资产位置
 */
export const approveTransfer = (id: number): Promise<ApiResponse<TransferRequest>> => {
  return api.post(`/transfers/${id}/approve`, { action: 'approve' });
};

/**
 * 拒绝调拨申请
 *
 * @param id - 调拨申请 ID
 * @param reason - 拒绝原因（可选）
 * @returns 更新后的调拨申请信息
 *
 * 权限：仅管理员可操作
 * 效果：状态变更为 rejected，资产位置不变
 */
export const rejectTransfer = (id: number, reason?: string): Promise<ApiResponse<TransferRequest>> => {
  return api.post(`/transfers/${id}/approve`, { action: 'reject', reason });
};

/**
 * 删除调拨申请
 *
 * @param id - 调拨申请 ID
 * @returns 空
 *
 * 注意：通常只能删除待审批状态的申请
 */
export const deleteTransfer = (id: number): Promise<ApiResponse<void>> => {
  return api.delete(`/transfers/${id}`);
};

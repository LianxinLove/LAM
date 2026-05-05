/**
 * 采购管理 API 接口
 *
 * 功能模块：
 * - 获取采购申请列表（支持分页、筛选）
 * - 获取采购申请详情
 * - 创建采购申请
 * - 更新采购申请
 * - 审批采购申请（批准/拒绝）
 *
 * 筛选参数（QueryParams）：
 * - status: 按状态筛选（pending/approved/purchased/rejected）
 * - applicant_id: 按申请人筛选
 * - my: 是否仅查看当前用户的申请（布尔值）
 *
 * 工作流程：
 * 1. 用户提交采购申请（status: pending）
 * 2. 管理员审批（status: approved/rejected）
 * 3. 采购完成后标记为已采购（status: purchased）
 */

import api from './index';
import type { PurchaseRequest, PurchaseFormData, ApiResponse, PaginatedResponse, QueryParams } from '../types';

/**
 * 获取采购申请列表
 *
 * @param params - 查询参数（分页、筛选）
 * @returns 分页的采购申请列表
 *
 * 使用示例：
 * ```ts
 * // 获取我的采购申请
 * const myPurchases = await getPurchases({ my: true });
 *
 * // 获取待审批的申请（管理员）
 * const pending = await getPurchases({ status: 'pending' });
 * ```
 */
export const getPurchases = (params?: QueryParams): Promise<ApiResponse<PaginatedResponse<PurchaseRequest>>> => {
  return api.get('/purchases', { params });
};

/**
 * 获取采购申请详情
 *
 * @param id - 采购申请 ID
 * @returns 采购申请详细信息
 */
export const getPurchase = (id: number): Promise<ApiResponse<PurchaseRequest>> => {
  return api.get(`/purchases/${id}`);
};

/**
 * 创建采购申请
 *
 * @param data - 采购申请信息
 * @returns 创建的采购申请信息
 *
 * 必填字段：product_name, product_code, quantity, purpose, project_name, delivery_info
 */
export const createPurchase = (data: PurchaseFormData): Promise<ApiResponse<PurchaseRequest>> => {
  return api.post('/purchases', data);
};

/**
 * 更新采购申请
 *
 * @param id - 采购申请 ID
 * @param data - 更新的采购申请信息
 * @returns 更新后的采购申请信息
 *
 * 注意：通常只能更新待审批状态的申请
 */
export const updatePurchase = (id: number, data: Partial<PurchaseFormData>): Promise<ApiResponse<PurchaseRequest>> => {
  return api.put(`/purchases/${id}`, data);
};

/**
 * 审批采购申请
 *
 * @param id - 采购申请 ID
 * @param action - 审批操作（approve/reject）
 * @param approval_comment - 审批意见
 * @returns 更新后的采购申请信息
 *
 * 权限：仅管理员可操作
 */
export const approvePurchase = (
  id: number,
  action: 'approve' | 'reject',
  approval_comment?: string
): Promise<ApiResponse<PurchaseRequest>> => {
  return api.post(`/purchases/${id}/approve`, { action, approval_comment });
};

/**
 * 批准采购申请
 *
 * @param id - 采购申请 ID
 * @param approval_comment - 审批意见（可选）
 * @returns 更新后的采购申请信息
 *
 * 权限：仅管理员可操作
 * 效果：状态变更为 approved，记录审批人和审批时间
 */
export const approvePurchaseRequest = (id: number, approval_comment?: string): Promise<ApiResponse<PurchaseRequest>> => {
  return api.post(`/purchases/${id}/approve`, { action: 'approve', approval_comment });
};

/**
 * 拒绝采购申请
 *
 * @param id - 采购申请 ID
 * @param approval_comment - 拒绝原因（可选）
 * @returns 更新后的采购申请信息
 *
 * 权限：仅管理员可操作
 * 效果：状态变更为 rejected，记录审批人、审批时间和拒绝原因
 */
export const rejectPurchaseRequest = (id: number, approval_comment?: string): Promise<ApiResponse<PurchaseRequest>> => {
  return api.post(`/purchases/${id}/approve`, { action: 'reject', approval_comment });
};

/**
 * 采购状态枚举值
 */
export const PurchaseStatuses = {
  PENDING: 'pending',
  APPROVED: 'approved',
  PURCHASED: 'purchased',
  REJECTED: 'rejected'
} as const;

/**
 * 采购状态标签映射
 */
export const PurchaseStatusLabel: Record<string, string> = {
  pending: '待审批',
  approved: '已审批',
  purchased: '已采购',
  rejected: '已拒绝'
};

/**
 * 采购状态颜色映射（用于Tag显示）
 */
export const PurchaseStatusColor: Record<string, string> = {
  pending: 'orange',
  approved: 'green',
  purchased: 'blue',
  rejected: 'red'
};

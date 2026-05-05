/**
 * 资产业务申请 API
 *
 * 处理保管人变更、资产调拨、设备维修、退库、报废、报失报损等业务
 */

import api from './index';
import type {
  AssetApplication,
  AssetApplicationFormData,
  ApiResponse,
  PaginatedResponse,
  QueryParams
} from '../types';

/**
 * 获取业务申请列表
 */
export async function getAssetApplications(params?: QueryParams): Promise<ApiResponse<PaginatedResponse<AssetApplication>>> {
  const searchParams = new URLSearchParams();
  if (params) {
    if (params.page) searchParams.append('page', params.page.toString());
    if (params.page_size) searchParams.append('page_size', params.page_size.toString());
    if (params.application_type) searchParams.append('application_type', params.application_type);
    if (params.status) searchParams.append('status', params.status);
    if (params.applicant_id) searchParams.append('applicant_id', params.applicant_id.toString());
    if (params.my) searchParams.append('my', 'true');
  }
  const query = searchParams.toString();
  return api.get(`/asset-applications${query ? `?${query}` : ''}`);
}

/**
 * 获取业务申请详情
 */
export async function getAssetApplication(id: number): Promise<ApiResponse<AssetApplication>> {
  return api.get(`/asset-applications/${id}`);
}

/**
 * 创建业务申请
 */
export async function createAssetApplication(data: AssetApplicationFormData): Promise<ApiResponse<AssetApplication>> {
  return api.post('/asset-applications', data);
}

/**
 * 审批业务申请（管理员）
 */
export async function approveAssetApplication(
  id: number,
  action: 'approve' | 'reject',
  approval_comment?: string
): Promise<ApiResponse<AssetApplication>> {
  return api.post(`/asset-applications/${id}/approve`, { action, approval_comment });
}

/**
 * 完成业务申请（管理员，用于维修完成后等场景）
 */
export async function completeAssetApplication(id: number): Promise<ApiResponse<AssetApplication>> {
  return api.post(`/asset-applications/${id}/complete`, {});
}

/**
 * 业务申请类型枚举值
 */
export const ApplicationTypes = {
  CUSTODIAN_CHANGE: 'custodian_change',
  ALLOCATION: 'allocation',
  REPAIR: 'repair',
  RETURN: 'return',
  SCRAP: 'scrap',
  LOSS: 'loss'
} as const;

/**
 * 业务申请状态枚举值
 */
export const ApplicationStatuses = {
  PENDING: 'pending',
  APPROVED: 'approved',
  REJECTED: 'rejected',
  PROCESSING: 'processing',
  COMPLETED: 'completed'
} as const;

/**
 * 业务申请类型标签映射
 */
export const ApplicationTypeLabels: Record<string, string> = {
  custodian_change: '保管人变更',
  allocation: '资产调拨',
  repair: '设备维修',
  return: '退库',
  scrap: '报废',
  loss: '报失报损'
};

/**
 * 业务申请状态标签映射
 */
export const ApplicationStatusLabel: Record<string, string> = {
  pending: '待审批',
  approved: '已审批',
  rejected: '已拒绝',
  processing: '处理中',
  completed: '已完成'
};

/**
 * 资产管理 API 接口
 *
 * 功能模块：
 * - 获取资产列表（支持分页、筛选）
 * - 获取资产详情
 * - 创建资产
 * - 更新资产
 * - 删除资产
 * - 资产管理人交接
 *
 * 筛选参数（QueryParams）：
 * - asset_type: 按资产类型筛选（equipment/software）
 * - status: 按状态筛选（in_use/scrapped/repair/returned/borrowed）
 * - campus: 按校区筛选
 * - manager_id: 按资产管理人筛选
 * - my_managed: 获取我保管的资产
 * - page: 页码
 * - page_size: 每页数量
 */

import api from './index';
import type { Asset, AssetLite, AssetFormData, ApiResponse, PaginatedResponse, QueryParams } from '../types';

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
 * // 按类型筛选
 * const equipment = await getAssets({ asset_type: 'equipment' });
 *
 * // 按状态筛选
 * const inUse = await getAssets({ status: 'in_use' });
 *
 * // 获取我保管的资产
 * const myAssets = await getAssets({ my_managed: true });
 * ```
 */
export const getAssets = (params?: QueryParams): Promise<ApiResponse<PaginatedResponse<AssetLite>>> => {
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
 * 创建资产（支持FormData，用于带图片上传）
 *
 * @param data - 资产信息（AssetFormData 或 FormData）
 * @returns 创建的资产信息
 *
 * 必填字段：lab_asset_code, name, asset_type, model, department, campus, building, custodian_name, custodian_phone, manager_id
 */
export const createAsset = (data: AssetFormData | FormData): Promise<ApiResponse<Asset>> => {
  return api.post('/assets', data);
};

/**
 * 更新资产（支持FormData，用于带图片上传）
 *
 * @param id - 资产 ID
 * @param data - 更新的资产信息（Partial<AssetFormData> 或 FormData）
 * @returns 更新后的资产信息
 */
export const updateAsset = (id: number, data: Partial<AssetFormData> | FormData): Promise<ApiResponse<Asset>> => {
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

/**
 * 资产管理人交接
 *
 * @param assetId - 资产 ID
 * @param data - 交接信息
 * @returns 交接记录信息
 */
export const transferAssetManager = (
  assetId: number,
  data: {
    new_manager_id: number;
    transfer_reason?: string;
    remarks?: string;
  }
): Promise<ApiResponse<any>> => {
  return api.post(`/assets/${assetId}/transfer-manager`, data);
};

/**
 * 资产类型枚举值
 */
export const AssetTypes = {
  EQUIPMENT: 'equipment',
  SOFTWARE: 'software'
} as const;

/**
 * 资产状态枚举值
 */
export const AssetStatuses = {
  IN_USE: 'in_use',
  SCRAPPED: 'scrapped',
  REPAIR: 'repair',
  RETURNED: 'returned',
  BORROWED: 'borrowed'
} as const;

/**
 * 资产类型标签映射
 */
export const AssetTypeLabels: Record<string, string> = {
  equipment: '仪器设备',
  software: '软件'
};

/**
 * 资产状态标签映射
 */
export const AssetStatusLabel: Record<string, string> = {
  in_use: '在用',
  scrapped: '报废',
  repair: '报修',
  returned: '退库',
  borrowed: '外借'
};

/**
 * 资产状态颜色映射（用于Tag显示）
 */
export const AssetStatusColor: Record<string, string> = {
  in_use: 'green',
  scrapped: 'default',
  repair: 'orange',
  returned: 'blue',
  borrowed: 'purple'
};

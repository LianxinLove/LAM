/**
 * 操作日志 API 接口
 *
 * 功能模块：
 * - 获取操作日志列表（支持分页、筛选）
 * - 获取操作日志详情
 *
 * 权限：仅管理员可访问
 *
 * 筛选参数（QueryParams）：
 * - user_id: 按用户筛选
 * - action: 按操作类型筛选
 * - model: 按数据模型筛选
 * - page: 页码
 * - page_size: 每页数量
 */

import api from './index';
import type { OperationLog, ApiResponse, PaginatedResponse, QueryParams } from '../types';

/**
 * 获取操作日志列表
 *
 * @param params - 查询参数（分页、筛选）
 * @returns 分页的操作日志列表
 *
 * 使用示例：
 * ```ts
 * // 获取所有操作日志
 * const logs = await getLogs();
 *
 * // 按用户筛选
 * const userLogs = await getLogs({ user_id: 1 });
 *
 * // 按操作类型筛选
 * const createLogs = await getLogs({ action: 'create' });
 * ```
 */
export const getLogs = (params?: QueryParams): Promise<ApiResponse<PaginatedResponse<OperationLog>>> => {
  return api.get('/logs', { params });
};

/**
 * 获取操作日志详情
 *
 * @param id - 操作日志 ID
 * @returns 操作日志详细信息
 */
export const getLog = (id: number): Promise<ApiResponse<OperationLog>> => {
  return api.get(`/logs/${id}`);
};

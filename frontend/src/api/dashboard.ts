/**
 * 仪表盘 API 接口
 *
 * 功能模块：
 * - 获取仪表盘统计数据
 *
 * 返回数据包括：
 * - 资产总数
 * - 耗材总数
 * - 我的借用数量
 * - 我的申请数量
 * - 低库存耗材列表
 * - 待审批采购数量（管理员）
 * - 待审批调拨数量（管理员）
 * - 待审批领用数量（管理员）
 */

import api from './index';
import type { DashboardData, ApiResponse } from '../types';

/**
 * 获取仪表盘数据
 *
 * @returns 仪表盘统计数据
 *
 * 技术要点：
 * - 根据用户角色返回不同的数据
 * - 普通用户：只看到自己的统计数据
 * - 管理员：看到全局统计数据和待审批项目
 */
export const getDashboardData = (): Promise<ApiResponse<DashboardData>> => {
  return api.get('/dashboard');
};

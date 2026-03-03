/**
 * 统计分析 API 接口
 *
 * 功能模块：
 * - 获取统计数据
 *
 * 返回数据包括：
 * - 按状态统计的资产数量
 * - 按类别统计的资产数量
 * - 耗材总价值
 * - 低库存耗材数量
 * - 按状态统计的采购申请数量
 * - 总预算金额
 * - 当前借用中的资产数量
 */

import api from './index';
import type { StatisticsData, ApiResponse } from '../types';

/**
 * 获取统计数据
 *
 * @returns 统计分析数据
 *
 * 技术要点：
 * - 聚合多个维度的统计数据
 * - 用于生成图表和报表
 */
export const getStatisticsData = (): Promise<ApiResponse<StatisticsData>> => {
  return api.get('/dashboard/statistics');
};

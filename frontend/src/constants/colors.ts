/**
 * 颜色常量
 * 统一管理项目中使用的颜色值
 */

// 健康状态相关颜色
export const HEALTH_COLORS = {
  EXCELLENT: '#52c41a', // 绿色 - 良好
  GOOD: '#faad14',      // 橙色 - 一般
  POOR: '#ff4d4f',      // 红色 - 较差
} as const;

// 健康状态阈值
export const HEALTH_THRESHOLDS = {
  EXCELLENT: 80, // >= 80 分为良好
  GOOD: 50,      // >= 50 分为一般
  PENALTY_PER_ITEM: 10, // 每个低库存项目扣除的分数
} as const;

// 图表颜色
export const CHART_COLORS = {
  PRIMARY: '#1890ff',
  SUCCESS: '#52c41a',
  WARNING: '#faad14',
  ERROR: '#ff4d4f',
  STATUS_COLORS: ['#fa8c16', '#1890ff', '#52c41a', '#ff4d4f'],
} as const;

// 间距常量
export const SPACING = {
  CARD_MARGIN: 24,
  EMPTY_STATE_PADDING: '60px 0',
} as const;

// 辅助函数：根据健康分数获取颜色和文本
export const getHealthStatus = (score: number) => {
  if (score >= HEALTH_THRESHOLDS.EXCELLENT) {
    return {
      color: HEALTH_COLORS.EXCELLENT,
      text: '良好',
      message: '库存状况良好，请继续保持',
    };
  }
  if (score >= HEALTH_THRESHOLDS.GOOD) {
    return {
      color: HEALTH_COLORS.GOOD,
      text: '一般',
      message: '部分耗材库存偏低，请关注',
    };
  }
  return {
    color: HEALTH_COLORS.POOR,
    text: '较差',
    message: '库存状况较差，请及时补充',
  };
};

// 计算健康分数
export const calculateHealthScore = (lowStockCount: number): number => {
  return lowStockCount === 0 ? 100 : Math.max(0, 100 - lowStockCount * HEALTH_THRESHOLDS.PENALTY_PER_ITEM);
};

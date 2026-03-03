import api from './index';
import type { StatisticsData, ApiResponse } from '../types';

// Get statistics data
export const getStatisticsData = (): Promise<ApiResponse<StatisticsData>> => {
  return api.get('/dashboard/statistics');
};

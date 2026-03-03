import api from './index';
import type { DashboardData, ApiResponse } from '../types';

// Get dashboard data
export const getDashboardData = (): Promise<ApiResponse<DashboardData>> => {
  return api.get('/dashboard');
};

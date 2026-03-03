import api from './index';
import type { OperationLog, ApiResponse, PaginatedResponse, QueryParams } from '../types';

// Get operation logs list
export const getLogs = (params?: QueryParams): Promise<ApiResponse<PaginatedResponse<OperationLog>>> => {
  return api.get('/logs', { params });
};

// Get operation log details
export const getLog = (id: number): Promise<ApiResponse<OperationLog>> => {
  return api.get(`/logs/${id}`);
};

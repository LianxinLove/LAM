import api from './index';
import type { PickRecord, PickFormData, ApiResponse, PaginatedResponse, QueryParams } from '../types';

// Get pick records list
export const getPicks = (params?: QueryParams): Promise<ApiResponse<PaginatedResponse<PickRecord>>> => {
  return api.get('/picks', { params });
};

// Get pick record details
export const getPick = (id: number): Promise<ApiResponse<PickRecord>> => {
  return api.get(`/picks/${id}`);
};

// Create pick request
export const createPick = (data: PickFormData): Promise<ApiResponse<PickRecord>> => {
  return api.post('/picks', data);
};

// Approve pick request
export const approvePick = (id: number): Promise<ApiResponse<PickRecord>> => {
  return api.post(`/picks/${id}/approve`, { action: 'approve' });
};

// Reject pick request
export const rejectPick = (id: number, reason?: string): Promise<ApiResponse<PickRecord>> => {
  return api.post(`/picks/${id}/approve`, { action: 'reject', reason });
};

// Delete pick record
export const deletePick = (id: number): Promise<ApiResponse<void>> => {
  return api.delete(`/picks/${id}`);
};

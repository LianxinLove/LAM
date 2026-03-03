import api from './index';
import type { TransferRequest, TransferFormData, ApiResponse, PaginatedResponse, QueryParams } from '../types';

// Get transfer requests list
export const getTransfers = (params?: QueryParams): Promise<ApiResponse<PaginatedResponse<TransferRequest>>> => {
  return api.get('/transfers', { params });
};

// Get transfer request details
export const getTransfer = (id: number): Promise<ApiResponse<TransferRequest>> => {
  return api.get(`/transfers/${id}`);
};

// Create transfer request
export const createTransfer = (data: TransferFormData): Promise<ApiResponse<TransferRequest>> => {
  return api.post('/transfers', data);
};

// Approve transfer request
export const approveTransfer = (id: number): Promise<ApiResponse<TransferRequest>> => {
  return api.post(`/transfers/${id}/approve`, { action: 'approve' });
};

// Reject transfer request
export const rejectTransfer = (id: number, reason?: string): Promise<ApiResponse<TransferRequest>> => {
  return api.post(`/transfers/${id}/approve`, { action: 'reject', reason });
};

// Delete transfer request
export const deleteTransfer = (id: number): Promise<ApiResponse<void>> => {
  return api.delete(`/transfers/${id}`);
};

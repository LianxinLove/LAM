import api from './index';
import type { PurchaseRequest, PurchaseFormData, ApiResponse, PaginatedResponse, QueryParams } from '../types';

// Get purchases list
export const getPurchases = (params?: QueryParams): Promise<ApiResponse<PaginatedResponse<PurchaseRequest>>> => {
  return api.get('/purchases', { params });
};

// Get purchase details
export const getPurchase = (id: number): Promise<ApiResponse<PurchaseRequest>> => {
  return api.get(`/purchases/${id}`);
};

// Create purchase request
export const createPurchase = (data: PurchaseFormData): Promise<ApiResponse<PurchaseRequest>> => {
  return api.post('/purchases', data);
};

// Update purchase
export const updatePurchase = (id: number, data: PurchaseFormData): Promise<ApiResponse<PurchaseRequest>> => {
  return api.put(`/purchases/${id}`, data);
};

// Delete purchase
export const deletePurchase = (id: number): Promise<ApiResponse<void>> => {
  return api.delete(`/purchases/${id}`);
};

// Approve purchase
export const approvePurchase = (id: number): Promise<ApiResponse<PurchaseRequest>> => {
  return api.post(`/purchases/${id}/approve`, { action: 'approve' });
};

// Reject purchase
export const rejectPurchase = (id: number, reason?: string): Promise<ApiResponse<PurchaseRequest>> => {
  return api.post(`/purchases/${id}/approve`, { action: 'reject', reason });
};

import api from './index';
import type { BorrowRecord, BorrowFormData, ApiResponse, PaginatedResponse, QueryParams } from '../types';

// Get borrow records list
export const getBorrows = (params?: QueryParams): Promise<ApiResponse<PaginatedResponse<BorrowRecord>>> => {
  return api.get('/borrows', { params });
};

// Get borrow record details
export const getBorrow = (id: number): Promise<ApiResponse<BorrowRecord>> => {
  return api.get(`/borrows/${id}`);
};

// Create borrow record
export const createBorrow = (data: BorrowFormData): Promise<ApiResponse<BorrowRecord>> => {
  return api.post('/borrows', data);
};

// Return asset
export const returnAsset = (id: number): Promise<ApiResponse<BorrowRecord>> => {
  return api.post(`/borrows/${id}/return`);
};

// Delete borrow record
export const deleteBorrow = (id: number): Promise<ApiResponse<void>> => {
  return api.delete(`/borrows/${id}`);
};

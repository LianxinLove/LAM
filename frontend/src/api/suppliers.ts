import api from './index';
import type { Supplier, ApiResponse, PaginatedResponse, QueryParams } from '../types';

// Get suppliers list
export const getSuppliers = (params?: QueryParams): Promise<ApiResponse<PaginatedResponse<Supplier>>> => {
  return api.get('/suppliers', { params });
};

// Get supplier details
export const getSupplier = (id: number): Promise<ApiResponse<Supplier>> => {
  return api.get(`/suppliers/${id}`);
};

// Create supplier
export const createSupplier = (data: {
  name: string;
  contact?: string;
  phone?: string;
  email?: string;
  address?: string;
}): Promise<ApiResponse<Supplier>> => {
  return api.post('/suppliers', data);
};

// Update supplier
export const updateSupplier = (id: number, data: {
  name: string;
  contact?: string;
  phone?: string;
  email?: string;
  address?: string;
}): Promise<ApiResponse<Supplier>> => {
  return api.put(`/suppliers/${id}`, data);
};

// Delete supplier
export const deleteSupplier = (id: number): Promise<ApiResponse<void>> => {
  return api.delete(`/suppliers/${id}`);
};

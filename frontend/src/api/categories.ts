import api from './index';
import type { Category, ApiResponse, PaginatedResponse, QueryParams } from '../types';

// Get categories list
export const getCategories = (params?: QueryParams): Promise<ApiResponse<PaginatedResponse<Category>>> => {
  return api.get('/categories', { params });
};

// Get category details
export const getCategory = (id: number): Promise<ApiResponse<Category>> => {
  return api.get(`/categories/${id}`);
};

// Create category
export const createCategory = (data: { name: string; parent_id?: number }): Promise<ApiResponse<Category>> => {
  return api.post('/categories', data);
};

// Update category
export const updateCategory = (id: number, data: { name: string; parent_id?: number }): Promise<ApiResponse<Category>> => {
  return api.put(`/categories/${id}`, data);
};

// Delete category
export const deleteCategory = (id: number): Promise<ApiResponse<void>> => {
  return api.delete(`/categories/${id}`);
};

import api from './index';
import type { Consumable, ConsumableFormData, ApiResponse, PaginatedResponse, QueryParams } from '../types';

// Get consumables list
export const getConsumables = (params?: QueryParams): Promise<ApiResponse<PaginatedResponse<Consumable>>> => {
  return api.get('/consumables', { params });
};

// Get consumable details
export const getConsumable = (id: number): Promise<ApiResponse<Consumable>> => {
  return api.get(`/consumables/${id}`);
};

// Create consumable
export const createConsumable = (data: ConsumableFormData): Promise<ApiResponse<Consumable>> => {
  return api.post('/consumables', data);
};

// Update consumable
export const updateConsumable = (id: number, data: ConsumableFormData): Promise<ApiResponse<Consumable>> => {
  return api.put(`/consumables/${id}`, data);
};

// Delete consumable
export const deleteConsumable = (id: number): Promise<ApiResponse<void>> => {
  return api.delete(`/consumables/${id}`);
};

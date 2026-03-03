import api from './index';
import type { Asset, AssetFormData, ApiResponse, PaginatedResponse, QueryParams } from '../types';

// Get assets list
export const getAssets = (params?: QueryParams): Promise<ApiResponse<PaginatedResponse<Asset>>> => {
  return api.get('/assets', { params });
};

// Get asset details
export const getAsset = (id: number): Promise<ApiResponse<Asset>> => {
  return api.get(`/assets/${id}`);
};

// Create asset
export const createAsset = (data: AssetFormData): Promise<ApiResponse<Asset>> => {
  return api.post('/assets', data);
};

// Update asset
export const updateAsset = (id: number, data: AssetFormData): Promise<ApiResponse<Asset>> => {
  return api.put(`/assets/${id}`, data);
};

// Delete asset
export const deleteAsset = (id: number): Promise<ApiResponse<void>> => {
  return api.delete(`/assets/${id}`);
};

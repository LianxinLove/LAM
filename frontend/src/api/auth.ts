import api from './index';
import type { LoginRequest, RegisterRequest, AuthResponse, ApiResponse } from '../types';

// Register user
export const register = (data: RegisterRequest): Promise<ApiResponse<AuthResponse>> => {
  return api.post('/auth/register', data);
};

// Login user
export const login = (data: LoginRequest): Promise<ApiResponse<AuthResponse>> => {
  return api.post('/auth/login', data);
};

// Get current user info
export const getCurrentUser = (): Promise<ApiResponse<any>> => {
  return api.get('/auth/me');
};

// Logout (client-side only)
export const logout = (): void => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

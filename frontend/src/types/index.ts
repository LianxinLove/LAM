// User Types
export interface User {
  id: number;
  username: string;
  email?: string;
  is_superuser: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  email?: string;
}

export interface AuthResponse {
  user_id: number;
  username: string;
  is_superuser: boolean;
  token: string;
}

// Asset Types
export interface Category {
  id: number;
  name: string;
  parent?: Category;
  created_at: string;
}

export interface Supplier {
  id: number;
  name: string;
  contact?: string;
  phone?: string;
  email?: string;
  address?: string;
  created_at: string;
}

export interface Asset {
  id: number;
  name: string;
  code: string;
  category: Category;
  supplier?: Supplier;
  specifications?: string;
  purchase_date?: string;
  purchase_price?: number;
  status: 'available' | 'in_use' | 'maintenance' | 'retired';
  location?: string;
  custodian?: string;  // Custodian name as string
  remarks?: string;
  created_at: string;
  updated_at: string;
}

export interface AssetFormData {
  name: string;
  code: string;
  category_id: number;
  supplier_id?: number;
  specifications?: string;
  purchase_date?: string;
  purchase_price?: number;
  location?: string;
  custodian?: string;  // Custodian name as string
  remarks?: string;
}

// Consumable Types
export interface Consumable {
  id: number;
  name: string;
  code: string;
  category: Category;
  supplier?: Supplier;
  unit: string;
  stock: number;
  min_stock: number;
  price?: number;
  location?: string;
  is_low_stock?: boolean;
  created_at: string;
  updated_at: string;
}

export interface ConsumableFormData {
  name: string;
  category_id: number;
  supplier_id?: number;
  unit: string;
  stock: number;
  min_stock: number;
  price?: number;
  location?: string;
}

// Purchase Request Types
export interface PurchaseRequest {
  id: number;
  title: string;
  applicant: User;
  item_name: string;
  quantity: number;
  estimated_price: number;
  supplier?: Supplier;
  reason: string;
  status: 'pending' | 'approved' | 'purchased' | 'rejected';
  approver?: User;
  approved_at?: string;
  created_at: string;
}

export interface PurchaseFormData {
  title: string;
  item_name: string;
  quantity: number;
  estimated_price: number;
  supplier_id?: number;
  reason: string;
}

// Borrow Record Types
export interface BorrowRecord {
  id: number;
  asset: Asset;
  borrower: User;
  borrow_date: string;
  return_date?: string;
  purpose?: string;
  status: 'borrowed' | 'returned';
}

export interface BorrowFormData {
  asset_id: number;
  purpose?: string;
}

// Pick Record Types
export interface PickRecord {
  id: number;
  item: Consumable;
  picker: User;
  quantity: number;
  purpose?: string;
  status: 'pending' | 'approved' | 'rejected';
  approver?: User;
  approved_at?: string;
  created_at: string;
}

export interface PickFormData {
  item_id: number;
  quantity: number;
  purpose?: string;
}

// Transfer Request Types
export interface TransferRequest {
  id: number;
  asset: Asset;
  from_location: string;
  to_location: string;
  reason: string;
  applicant: User;
  status: 'pending' | 'approved' | 'rejected';
  approver?: User;
  approved_at?: string;
  created_at: string;
}

export interface TransferFormData {
  asset_id: number;
  to_location: string;
  reason: string;
}

// Operation Log Types
export interface OperationLog {
  id: number;
  user: User;
  action: string;
  model: string;
  object_id: number;
  object_repr: string;
  details?: string;
  timestamp: string;
}

// Dashboard Types
export interface DashboardData {
  asset_count: number;
  consumable_count: number;
  my_borrows: number;
  my_requests: number;
  low_stock_items: Consumable[];
  pending_purchases?: number;
  pending_transfers?: number;
  pending_picks?: number;
}

// Statistics Types
export interface StatisticsData {
  asset_by_status: Array<{ status: string; count: number }>;
  asset_by_category: Array<{ category: string; count: number }>;
  total_consumable_value: number;
  low_stock_count: number;
  purchase_by_status: Array<{ status: string; count: number }>;
  total_budget: number;
  active_borrows: number;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface ApiError {
  success: false;
  message: string;
  error_code?: string;
  details?: any;
}

// Query Params Types
export interface QueryParams {
  page?: number;
  page_size?: number;
  category_id?: number;
  status?: string;
  low_stock?: boolean;
  my?: boolean;
  applicant_id?: number;
}

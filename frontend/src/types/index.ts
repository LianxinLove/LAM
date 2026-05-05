/**
 * 全局类型定义
 *
 * 说明：
 * - 定义系统中使用的所有 TypeScript 接口和类型
 * - 与后端 API 数据结构保持一致
 * - 使用严格的类型检查提高代码可靠性
 */

// ==================== 用户认证类型 ====================

/**
 * 用户信息
 */
export interface User {
  /** 用户 ID */
  id: number;
  /** 用户名 */
  username: string;
  /** 电子邮箱（可选） */
  email?: string;
  /** 是否为超级用户（管理员） */
  is_superuser: boolean;
}

/**
 * 登录请求
 */
export interface LoginRequest {
  /** 用户名 */
  username: string;
  /** 密码 */
  password: string;
}

/**
 * 注册请求
 */
export interface RegisterRequest {
  /** 用户名 */
  username: string;
  /** 密码 */
  password: string;
  /** 电子邮箱（可选） */
  email?: string;
}

/**
 * 认证响应
 *
 * 后端登录/注册成功后返回的数据
 *
 * 认证方式：Session-Cookie
 * - Session ID 通过 Cookie 返回，由浏览器自动管理
 * - 不需要在响应中包含 token
 */
export interface AuthResponse {
  /** 用户 ID */
  user_id: number;
  /** 用户名 */
  username: string;
  /** 是否为管理员 */
  is_superuser: boolean;
}

// ==================== 资产相关类型 ====================

/**
 * 资产类别
 *
 * 支持树形结构，通过 parent 字段关联父类别
 */
export interface Category {
  /** 类别 ID */
  id: number;
  /** 类别名称 */
  name: string;
  /** 父类别（可选，用于构建层级结构） */
  parent?: Category;
  /** 创建时间 */
  created_at: string;
}

/**
 * 供应商信息
 */
export interface Supplier {
  /** 供应商 ID */
  id: number;
  /** 供应商名称 */
  name: string;
  /** 联系人 */
  contact?: string;
  /** 联系电话 */
  phone?: string;
  /** 电子邮箱 */
  email?: string;
  /** 地址 */
  address?: string;
  /** 创建时间 */
  created_at: string;
}

/**
 * 资产类型枚举
 */
export type AssetType = 'equipment' | 'software';

/**
 * 资产状态枚举
 */
export type AssetStatus = 'in_use' | 'scrapped' | 'repair' | 'returned' | 'borrowed';

/**
 * 资产信息（简化版 - 用于列表展示）
 */
export interface AssetLite {
  /** 资产 ID */
  id: number;
  /** 课题组资产编号（格式：DC+年份+序号） */
  lab_asset_code: string;
  /** 资产名称 */
  name: string;
  /** 院系归属 */
  department: string;
  /** 资产状态 */
  current_status: AssetStatus;
  /** 存放位置（组合字段，方便显示） */
  location: string;
  /** 课题组保管人姓名 */
  custodian_name: string;
  /** 资产管理人 */
  manager: User;
}

/**
 * 资产信息（完整版 - 用于详情和编辑）
 */
export interface Asset {
  /** 资产 ID */
  id: number;
  /** 课题组资产编号（格式：DC+年份+序号） */
  lab_asset_code: string;
  /** 学校资产编号（可选） */
  school_asset_code?: string;
  /** 资产名称 */
  name: string;
  /** 资产类型 */
  asset_type: AssetType;
  /** 型号 */
  model: string;
  /** 规格 */
  specifications?: string;
  /** 生产厂家 */
  manufacturer?: string;
  /** 采购价格 */
  purchase_price?: number;
  /** 院系归属 */
  department: string;
  /** 资产状态 */
  current_status: AssetStatus;
  /** 存放校区 */
  campus: string;
  /** 存放楼宇 */
  building: string;
  /** 存放房间（可选） */
  room?: string;
  /** 存放位置（组合字段，方便显示） */
  location?: string;
  /** 采购日期（ISO 8601 格式） */
  purchase_date?: string;
  /** 课题组保管人姓名 */
  custodian_name: string;
  /** 课题组保管人联系电话 */
  custodian_phone: string;
  /** 资产管理人 */
  manager: User;
  /** 资产全貌照片URL */
  photo_full_url?: string;
  /** 资产型号铭牌近照URL */
  photo_model_url?: string;
  /** 学校固定资产铭牌近照URL */
  photo_tag_url?: string;
  /** 备注 */
  remarks?: string;
  /** 创建时间 */
  created_at: string;
  /** 更新时间 */
  updated_at: string;
}

/**
 * 资产表单数据
 *
 * 用于创建和更新资产
 */
export interface AssetFormData {
  /** 课题组资产编号（必填） */
  lab_asset_code: string;
  /** 学校资产编号（可选） */
  school_asset_code?: string;
  /** 资产名称（必填） */
  name: string;
  /** 资产类型（必填） */
  asset_type: AssetType;
  /** 型号（必填） */
  model: string;
  /** 规格 */
  specifications?: string;
  /** 生产厂家 */
  manufacturer?: string;
  /** 采购价格 */
  purchase_price?: number;
  /** 院系归属（必填） */
  department: string;
  /** 资产状态 */
  current_status?: AssetStatus;
  /** 存放校区（必填） */
  campus: string;
  /** 存放楼宇（必填） */
  building: string;
  /** 存放房间 */
  room?: string;
  /** 采购日期（YYYY-MM-DD 格式） */
  purchase_date?: string;
  /** 课题组保管人姓名（必填） */
  custodian_name: string;
  /** 课题组保管人联系电话（必填） */
  custodian_phone: string;
  /** 资产管理人ID（必填） */
  manager_id: number;
  /** 资产全貌照片URL */
  photo_full_url?: string;
  /** 资产型号铭牌近照URL */
  photo_model_url?: string;
  /** 学校固定资产铭牌近照URL */
  photo_tag_url?: string;
  /** 备注 */
  remarks?: string;
}

// ==================== 耗材相关类型 ====================

/**
 * 耗材形态枚举
 */
export type ConsumableForm = 'solid' | 'liquid' | 'gas';

/**
 * 耗材分类枚举
 */
export type ConsumableType = 'consumable' | 'reagent';

/**
 * 耗材信息
 */
export interface Consumable {
  /** 耗材 ID */
  id: number;
  /** 耗材名称 */
  name: string;
  /** 耗材编号 */
  code: string;
  /** 所属类别 */
  category: Category;
  /** 供应商（可选） */
  supplier?: Supplier;
  /** 品牌 */
  brand?: string;
  /** 货号 */
  product_code: string;
  /** CAS号 */
  cas_number?: string;
  /** 形态 */
  form?: ConsumableForm;
  /** 分类（耗材/试剂） */
  consumable_type: ConsumableType;
  /** 是否危化品 */
  is_hazardous: boolean;
  /** 规格 */
  specifications?: string;
  /** 当前库存数量 */
  stock: number;
  /** 最低库存警戒线 */
  min_stock: number;
  /** 课题组保管人 */
  custodian_name: string;
  /** 课题组保管人联系方式 */
  custodian_phone: string;
  /** 产品最早生产日期 */
  production_date?: string;
  /** 产品保质期 */
  expiration_date?: string;
  /** 是否过期 */
  is_expired?: boolean;
  /** 存放区域 */
  storage_area?: string;
  /** 存放房间 */
  room?: string;
  /** 存放楼宇 */
  building?: string;
  /** 存放校区 */
  campus?: string;
  /** 单价 */
  price?: number;
  /** 备注 */
  remarks?: string;
  /** 是否低库存（库存 < 最低库存） */
  is_low_stock?: boolean;
  /** 创建时间 */
  created_at: string;
  /** 更新时间 */
  updated_at: string;
}

/**
 * 耗材表单数据
 *
 * 用于创建和更新耗材
 */
export interface ConsumableFormData {
  /** 耗材名称（必填） */
  name: string;
  /** 类别 ID（必填） */
  category_id: number;
  /** 供应商 ID（可选） */
  supplier_id?: number;
  /** 品牌 */
  brand?: string;
  /** 货号（必填） */
  product_code: string;
  /** CAS号 */
  cas_number?: string;
  /** 形态 */
  form?: ConsumableForm;
  /** 分类（耗材/试剂） */
  consumable_type?: ConsumableType;
  /** 是否危化品 */
  is_hazardous?: boolean;
  /** 规格 */
  specifications?: string;
  /** 初始库存（必填） */
  stock?: number;
  /** 最低库存（必填） */
  min_stock?: number;
  /** 课题组保管人（必填） */
  custodian_name: string;
  /** 课题组保管人联系方式（必填） */
  custodian_phone: string;
  /** 产品最早生产日期 */
  production_date?: string;
  /** 产品保质期 */
  expiration_date?: string;
  /** 存放区域 */
  storage_area?: string;
  /** 存放房间 */
  room?: string;
  /** 存放楼宇 */
  building?: string;
  /** 存放校区 */
  campus?: string;
  /** 单价 */
  price?: number;
  /** 备注 */
  remarks?: string;
}

// ==================== 采购申请类型 ====================

/**
 * 采购申请状态
 */
export type PurchaseStatus = 'pending' | 'approved' | 'purchased' | 'rejected';

/**
 * 采购申请信息
 */
export interface PurchaseRequest {
  /** 申请 ID */
  id: number;
  /** 序号 */
  sequence_number: number;
  /** 产品名称 */
  product_name: string;
  /** 品牌 */
  brand?: string;
  /** 货号 */
  product_code: string;
  /** CAS号 */
  cas_number?: string;
  /** 形态 */
  form?: string;
  /** 规格 */
  specifications?: string;
  /** 数量 */
  quantity: number;
  /** 用途 */
  purpose: string;
  /** 申请人 */
  applicant: User;
  /** 申请项目 */
  project_name: string;
  /** 申请日期 */
  application_date: string;
  /** 申请人收货信息 */
  delivery_info: string;
  /** 查询单价 */
  query_price?: number;
  /** 订购单价 */
  order_price?: number;
  /** 订购数量 */
  order_quantity?: number;
  /** 到货日期 */
  delivery_date?: string;
  /** 到货数量 */
  delivery_quantity?: number;
  /** 存放校区 */
  campus?: string;
  /** 存放楼宇 */
  building?: string;
  /** 存放房间 */
  room?: string;
  /** 是否危化品平台采购 */
  is_hazardous_platform?: boolean;
  /** 是否生科院试剂中心采购 */
  is_institute_center?: boolean;
  /** 是否学校仓库采购 */
  is_school_warehouse?: boolean;
  /** 质量问题说明及证据 */
  quality_issue_info?: string;
  /** 备注 */
  remarks?: string;
  /** 申请状态 */
  status: PurchaseStatus;
  /** 审批人（可选） */
  approver?: User;
  /** 审批意见 */
  approval_comment?: string;
  /** 审批时间（可选） */
  approved_at?: string;
  /** 创建时间 */
  created_at: string;
}

/**
 * 采购申请表单数据
 */
export interface PurchaseFormData {
  /** 产品名称（必填） */
  product_name: string;
  /** 品牌 */
  brand?: string;
  /** 货号（必填） */
  product_code: string;
  /** CAS号 */
  cas_number?: string;
  /** 形态 */
  form?: string;
  /** 规格 */
  specifications?: string;
  /** 数量（必填） */
  quantity: number;
  /** 用途（必填） */
  purpose: string;
  /** 申请项目（必填） */
  project_name: string;
  /** 申请人收货信息（必填） */
  delivery_info: string;
  /** 查询单价 */
  query_price?: number;
  /** 存放校区 */
  campus?: string;
  /** 存放楼宇 */
  building?: string;
  /** 存放房间 */
  room?: string;
  /** 是否危化品平台采购 */
  is_hazardous_platform?: boolean;
  /** 是否生科院试剂中心采购 */
  is_institute_center?: boolean;
  /** 是否学校仓库采购 */
  is_school_warehouse?: boolean;
  /** 备注 */
  remarks?: string;
}

// ==================== 资产借用类型 ====================

/**
 * 借用记录状态
 */
export type BorrowStatus = 'borrowed' | 'returned';

/**
 * 资产借用记录
 */
export interface BorrowRecord {
  /** 借用记录 ID */
  id: number;
  /** 被借用的资产 */
  asset: Asset;
  /** 借用人 */
  borrower: User;
  /** 借用日期 */
  borrow_date: string;
  /** 归还日期（已归还时） */
  return_date?: string;
  /** 用途说明 */
  purpose?: string;
  /** 借用状态 */
  status: BorrowStatus;
}

/**
 * 借用表单数据
 */
export interface BorrowFormData {
  /** 资产 ID（必填） */
  asset_id: number;
  /** 用途说明（可选） */
  purpose?: string;
}

// ==================== 耗材领用类型 ====================

/**
 * 领用申请状态
 */
export type PickStatus = 'pending' | 'approved' | 'rejected';

/**
 * 耗材领用记录
 */
export interface PickRecord {
  /** 领用记录 ID */
  id: number;
  /** 领用的耗材 */
  item: Consumable;
  /** 领用人 */
  picker: User;
  /** 领用数量 */
  quantity: number;
  /** 用途说明 */
  purpose?: string;
  /** 申请状态 */
  status: PickStatus;
  /** 审批人（可选） */
  approver?: User;
  /** 审批时间（可选） */
  approved_at?: string;
  /** 创建时间 */
  created_at: string;
}

/**
 * 领用表单数据
 */
export interface PickFormData {
  /** 耗材 ID（必填） */
  item_id: number;
  /** 领用数量（必填） */
  quantity: number;
  /** 用途说明（可选） */
  purpose?: string;
}

// ==================== 资产调拨类型 ====================

/**
 * 调拨申请状态
 */
export type TransferStatus = 'pending' | 'approved' | 'rejected';

/**
 * 资产调拨申请
 */
export interface TransferRequest {
  /** 调拨申请 ID */
  id: number;
  /** 调拨的资产 */
  asset: Asset;
  /** 原校区 */
  from_campus: string;
  /** 原楼宇 */
  from_building: string;
  /** 原房间 */
  from_room?: string;
  /** 原位置（组合字段） */
  from_location: string;
  /** 目标校区 */
  to_campus: string;
  /** 目标楼宇 */
  to_building: string;
  /** 目标房间 */
  to_room?: string;
  /** 目标位置（组合字段） */
  to_location: string;
  /** 调拨原因 */
  reason: string;
  /** 申请人 */
  applicant: User;
  /** 申请状态 */
  status: TransferStatus;
  /** 接收确认人（可选） */
  receiver?: User;
  /** 审批人（可选） */
  approver?: User;
  /** 审批时间（可选） */
  approved_at?: string;
  /** 创建时间 */
  created_at: string;
}

/**
 * 调拨表单数据
 */
export interface TransferFormData {
  /** 资产 ID（必填） */
  asset_id: number;
  /** 目标校区（必填） */
  to_campus: string;
  /** 目标楼宇（必填） */
  to_building: string;
  /** 目标房间（可选） */
  to_room?: string;
  /** 调拨原因（必填） */
  reason: string;
}

// ==================== 资产业务申请类型 ====================

/**
 * 业务申请类型
 */
export type ApplicationType = 'custodian_change' | 'allocation' | 'repair' | 'return' | 'scrap' | 'loss';

/**
 * 业务申请状态
 */
export type ApplicationStatus = 'pending' | 'approved' | 'rejected' | 'processing' | 'completed';

/**
 * 资产业务申请
 */
export interface AssetApplication {
  /** 申请 ID */
  id: number;
  /** 资产 */
  asset: Asset;
  /** 申请类型 */
  application_type: ApplicationType;
  /** 申请人 */
  applicant: User;
  /** 申请人姓名 */
  applicant_name: string;
  /** 申请时间 */
  application_time: string;
  /** 状态 */
  status: ApplicationStatus;
  /** 申请内容（JSON对象，不同类型有不同字段） */
  content: Record<string, any>;
  /** 审批意见 */
  approval_comment?: string;
  /** 审批人 */
  approver?: User;
  /** 审批时间 */
  approval_time?: string;
  /** 创建时间 */
  created_at: string;
  /** 更新时间 */
  updated_at: string;
}

/**
 * 业务申请表单数据
 */
export interface AssetApplicationFormData {
  /** 资产 ID（必填） */
  asset_id: number;
  /** 申请类型（必填） */
  application_type: ApplicationType;
  /** 新保管人ID（保管人变更时必填） */
  new_custodian_id?: number;
  /** 新位置信息（资产调拨时必填） */
  campus?: string;
  building?: string;
  room?: string;
  /** 故障描述（设备维修时必填） */
  fault_description?: string;
  /** 原因（所有类型都需要） */
  reason?: string;
  /** 备注 */
  notes?: string;
}

// ==================== 操作日志类型 ====================

/**
 * 操作日志
 */
export interface OperationLog {
  /** 日志 ID */
  id: number;
  /** 操作用户 */
  user: User;
  /** 操作类型（create/update/delete 等） */
  action: string;
  /** 操作的数据模型 */
  model: string;
  /** 操作对象的 ID */
  object_id: number;
  /** 操作对象的字符串表示 */
  object_repr: string;
  /** 详细信息（可选） */
  details?: string;
  /** 操作时间 */
  timestamp: string;
}

// ==================== 仪表盘类型 ====================

/**
 * 仪表盘统计数据
 */
export interface DashboardData {
  /** 资产总数 */
  asset_count: number;
  /** 耗材总数 */
  consumable_count: number;
  /** 我的借用数量 */
  my_borrows: number;
  /** 我的申请数量 */
  my_requests: number;
  /** 低库存耗材列表 */
  low_stock_items: Consumable[];
  /** 过期耗材列表 */
  expired_items: Consumable[];
  /** 待审批采购数（管理员） */
  pending_purchases?: number;
  /** 待审批调拨数（管理员） */
  pending_transfers?: number;
  /** 待审批领用数（管理员） */
  pending_picks?: number;
}

// ==================== 统计分析类型 ====================

/**
 * 统计分析数据
 */
export interface StatisticsData {
  /** 按状态统计的资产数量 */
  asset_by_status: Array<{ status: string; count: number }>;
  /** 按类型统计的资产数量 */
  asset_by_type: Array<{ type: string; count: number }>;
  /** 按院系统计的资产数量 */
  asset_by_department: Array<{ department: string; count: number }>;
  /** 按校区统计的资产数量 */
  asset_by_campus: Array<{ campus: string; count: number }>;
  /** 耗材总价值 */
  total_consumable_value: number;
  /** 低库存耗材数量 */
  low_stock_count: number;
  /** 过期耗材数量 */
  expired_count: number;
  /** 按状态统计的采购申请数量 */
  purchase_by_status: Array<{ status: string; count: number }>;
  /** 总预算金额 */
  total_budget: number;
  /** 当前借用中的资产数量 */
  active_borrows: number;
}

// ==================== API 响应类型 ====================

/**
 * 通用 API 响应
 *
 * @template T - 响应数据的类型
 */
export interface ApiResponse<T> {
  /** 请求是否成功 */
  success: boolean;
  /** 响应消息 */
  message: string;
  /** 响应数据 */
  data: T;
}

/**
 * 分页响应数据
 *
 * @template T - 列表项的类型
 */
export interface PaginatedResponse<T> {
  /** 数据列表 */
  items: T[];
  /** 总记录数 */
  total: number;
  /** 当前页码 */
  page: number;
  /** 每页数量 */
  page_size: number;
}

/**
 * API 错误响应
 */
export interface ApiError {
  /** 请求是否失败（固定为 false） */
  success: false;
  /** 错误消息 */
  message: string;
  /** 错误代码（可选） */
  error_code?: string;
  /** 错误详情（可选） */
  details?: any;
}

// ==================== 查询参数类型 ====================

/**
 * 通用查询参数
 *
 * 用于列表 API 的筛选和分页
 */
export interface QueryParams {
  /** 页码（从 1 开始） */
  page?: number;
  /** 每页数量 */
  page_size?: number;
  /** 按类别筛选 */
  category_id?: number;
  /** 按状态筛选 */
  status?: string;
  /** 仅显示低库存项目（耗材） */
  low_stock?: boolean;
  /** 仅显示过期项目（耗材） */
  is_expired?: boolean;
  /** 仅显示当前用户的记录 */
  my?: boolean;
  /** 按申请人筛选 */
  applicant_id?: number;
  /** 按资产类型筛选 */
  asset_type?: AssetType;
  /** 按耗材分类筛选 */
  consumable_type?: ConsumableType;
}

/**
 * 状态文本映射常量
 * 统一管理各种状态的中文翻译，避免在多个文件中重复定义
 */

// 资产状态
export const ASSET_STATUS_TEXTS = {
  available: '可用',
  in_use: '使用中',
  maintenance: '维修中',
  retired: '已报废',
} as const;

// 采购申请状态
export const PURCHASE_STATUS_TEXTS = {
  pending: '待审批',
  approved: '已审批',
  purchased: '已采购',
  rejected: '已拒绝',
} as const;

// 领用申请状态
export const PICK_STATUS_TEXTS = {
  pending: '待审批',
  approved: '已审批',
  rejected: '已拒绝',
} as const;

// 调拨申请状态
export const TRANSFER_STATUS_TEXTS = {
  pending: '待审批',
  approved: '已审批',
  rejected: '已拒绝',
} as const;

// 借用状态
export const BORROW_STATUS_TEXTS = {
  borrowed: '借用中',
  returned: '已归还',
} as const;

// 辅助函数：获取状态文本
export const getAssetStatusText = (status: string): string => ASSET_STATUS_TEXTS[status as keyof typeof ASSET_STATUS_TEXTS] || status;
export const getPurchaseStatusText = (status: string): string => PURCHASE_STATUS_TEXTS[status as keyof typeof PURCHASE_STATUS_TEXTS] || status;
export const getPickStatusText = (status: string): string => PICK_STATUS_TEXTS[status as keyof typeof PICK_STATUS_TEXTS] || status;
export const getTransferStatusText = (status: string): string => TRANSFER_STATUS_TEXTS[status as keyof typeof TRANSFER_STATUS_TEXTS] || status;
export const getBorrowStatusText = (status: string): string => BORROW_STATUS_TEXTS[status as keyof typeof BORROW_STATUS_TEXTS] || status;

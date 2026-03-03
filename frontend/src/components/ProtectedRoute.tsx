/**
 * 路由保护组件
 *
 * 功能说明：
 * 1. 验证用户是否已登录
 * 2. 可选验证用户是否为管理员
 * 3. 未授权时自动重定向到登录页或仪表盘
 *
 * 技术要点：
 * - 使用 React Router 的 Navigate 组件实现重定向
 * - 保存原始访问路径，登录后可返回
 * - 加载状态处理
 *
 * 使用方式：
 * ```tsx
 * // 需要登录
 * <ProtectedRoute><PrivatePage /></ProtectedRoute>
 *
 * // 需要管理员权限
 * <ProtectedRoute adminOnly><AdminPage /></ProtectedRoute>
 * ```
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Spin } from 'antd';
import { useAuth } from '../contexts/AuthContext';

/**
 * ProtectedRoute 组件属性
 */
interface ProtectedRouteProps {
  /** 子组件，即要保护的路由内容 */
  children: React.ReactNode;
  /** 是否仅管理员可访问，默认 false */
  adminOnly?: boolean;
}

/**
 * ProtectedRoute 组件
 *
 * @param props - 组件属性
 * @returns 保护后的路由内容或重定向组件
 *
 * 认证流程：
 * 1. 检查加载状态：显示加载动画
 * 2. 检查登录状态：未登录则跳转登录页
 * 3. 检查管理员权限：非管理员访问管理页面则跳转仪表盘
 * 4. 通过所有验证：渲染子组件
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  adminOnly = false,
}) => {
  // 获取认证状态
  const { user, loading, isAdmin } = useAuth();

  // 获取当前路径，用于登录后重定向回来
  const location = useLocation();

  // ========== 加载状态 ==========

  /**
   * 认证状态初始化中
   *
   * 技术要点：
   * - 防止闪烁：在验证 token 期间显示加载状态
   * - 使用 Ant Design 的 Spin 组件提供友好的加载体验
   */
  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh'
      }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  // ========== 登录验证 ==========

  /**
   * 用户未登录
   *
   * 技术要点：
   * - Navigate 组件实现声明式导航
   * - state.from 保存原始路径，登录后可返回
   * - replace 避免用户按后退键又回到需要登录的页面
   */
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // ========== 管理员权限验证 ==========

  /**
   * 非管理员访问管理页面
   *
   * 技术要点：
   * - 重定向到仪表盘而非登录页
   * - 避免让已登录用户感到困惑
   */
  if (adminOnly && !isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  // ========== 验证通过 ==========

  /**
   * 所有验证通过，渲染受保护的内容
   */
  return <>{children}</>;
};

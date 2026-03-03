/**
 * 认证上下文模块
 *
 * 认证方式：Session-Cookie
 *
 * 功能说明：
 * 1. 管理用户认证状态（登录/未登录）
 * 2. 提供认证相关方法（登录、注册、登出）
 * 3. 提供用户信息和权限状态
 * 4. 刷新页面时自动恢复登录状态
 *
 * 技术要点：
 * - 使用 React Context API 实现全局状态共享
 * - Session ID 存储在 Cookie 中，由浏览器自动管理
 * - 通过调用 /auth/me API 验证 Session 有效性
 * - 响应式拦截 401 错误，自动跳转登录页
 *
 * 使用方式：
 * ```tsx
 * // 在组件中使用 Hook
 * const { user, isAdmin, login, logout } = useAuth();
 *
 * // 在路由中使用 ProtectedRoute 组件
 * <ProtectedRoute><PrivatePage /></ProtectedRoute>
 * ```
 */

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { message } from 'antd';
import { login as loginApi, register as registerApi, getCurrentUser, logout as logoutApi } from '../api/auth';
import type { User, LoginRequest, RegisterRequest } from '../types';

/**
 * 认证上下文类型定义
 */
interface AuthContextType {
  /** 当前登录用户信息，未登录时为 null */
  user: User | null;
  /** 加载状态，用于初始化时显示加载动画 */
  loading: boolean;
  /** 登录方法 */
  login: (credentials: LoginRequest) => Promise<void>;
  /** 注册方法 */
  register: (data: RegisterRequest) => Promise<void>;
  /** 登出方法 */
  logout: () => void;
  /** 是否为管理员 */
  isAdmin: boolean;
}

/**
 * 创建认证上下文
 *
 * 技术要点：
 * - createContext 创建上下文对象
 * - 默认值为 undefined，用于检测是否在 Provider 内部使用
 */
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * useAuth Hook
 *
 * 功能：在组件中访问认证上下文
 *
 * 技术要点：
 * - 使用 useContext Hook 获取上下文值
 * - 防御性编程：如果在 Provider 外部使用则抛出错误
 *
 * @throws {Error} 如果在 AuthProvider 外部使用
 * @returns {AuthContextType} 认证上下文值
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { user, isAdmin, logout } = useAuth();
 *   return <div>Welcome, {user?.username}</div>;
 * }
 * ```
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

/**
 * AuthProvider 组件属性类型
 */
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * AuthProvider 组件
 *
 * 功能：
 * 1. 封装认证状态和逻辑
 * 2. 应用初始化时自动验证 Session 并恢复登录状态
 * 3. 提供认证相关方法给子组件
 *
 * 技术要点：
 * - 使用 useEffect 实现初始化时验证 Session
 * - 调用 /auth/me API 验证 Session 有效性
 * - Session 过期时由 API 拦截器处理跳转
 *
 * @example
 * ```tsx
 * <AuthProvider>
 *   <App />
 * </AuthProvider>
 * ```
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  // ========== 状态管理 ==========

  /** 当前用户信息 */
  const [user, setUser] = useState<User | null>(null);

  /** 初始化加载状态 */
  const [loading, setLoading] = useState(true);

  const navigate = useNavigate();

  // ========== 副作用：初始化认证状态 ==========

  /**
   * 应用初始化时验证 Session 并恢复登录状态
   *
   * 技术要点：
   * - useEffect 空依赖数组，仅在组件挂载时执行一次
   * - 调用 /auth/me API 验证 Session 有效性
   * - Cookie 中的 session_id 由浏览器自动携带
   * - 成功则设置用户状态，失败则 Session 已过期
   * - 如果当前在登录页，不调用 API 避免无限循环
   */
  useEffect(() => {
    // 如果当前在登录页，不调用 API，直接完成加载
    if (window.location.pathname === '/login') {
      setLoading(false);
      return;
    }

    getCurrentUser()
      .then((response) => {
        if (response.success) {
          setUser(response.data);
        }
        // Session 过期时不需要额外处理，API 拦截器会处理跳转
      })
      .catch(() => {
        // API 调用失败（Session 过期），清空用户状态
        setUser(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  // ========== 认证方法 ==========

  /**
   * 用户登录
   *
   * @param credentials - 登录凭据（用户名、密码）
   *
   * 流程：
   * 1. 调用登录 API
   * 2. 后端创建 Session 并通过 Cookie 返回 session_id
   * 3. 更新用户状态
   * 4. 跳转到仪表盘
   *
   * 技术要点：
   * - 使用 useCallback 避免不必要的函数重建
   * - Session ID 由浏览器自动存储在 Cookie 中
   * - 不需要手动存储 token
   */
  const login = useCallback(async (credentials: LoginRequest) => {
    try {
      const response = await loginApi(credentials);
      if (response.success) {
        // 更新用户状态
        setUser({
          id: response.data.user_id,
          username: response.data.username,
          is_superuser: response.data.is_superuser,
        });
        message.success('登录成功');
        navigate('/dashboard');
      } else {
        message.error(response.message || '登录失败');
      }
    } catch (error: any) {
      // 显示后端返回的错误信息
      message.error(error.message || '登录失败');
    }
  }, [navigate]);

  /**
   * 用户注册
   *
   * @param data - 注册信息（用户名、密码、邮箱）
   *
   * 流程：
   * 1. 调用注册 API
   * 2. 注册成功后自动登录，后端创建 Session
   * 3. 更新用户状态
   * 4. 跳转到仪表盘
   */
  const register = useCallback(async (data: RegisterRequest) => {
    try {
      const response = await registerApi(data);
      if (response.success) {
        // 更新用户状态
        setUser({
          id: response.data.user_id,
          username: response.data.username,
          is_superuser: response.data.is_superuser,
        });
        message.success('注册成功');
        navigate('/dashboard');
      } else {
        message.error(response.message || '注册失败');
      }
    } catch (error: any) {
      // 显示后端返回的错误信息
      message.error(error.message || '注册失败');
    }
  }, [navigate]);

  /**
   * 用户登出
   *
   * 流程：
   * 1. 调用后端登出 API，清除服务端 Session
   * 2. 清空用户状态
   * 3. 跳转到登录页
   *
   * 技术要点：
   * - 调用后端 API 清除 Session
   * - Cookie 中的 session_id 会被标记为过期
   * - 浏览器会自动清理过期的 Cookie
   */
  const logout = useCallback(async () => {
    try {
      // 调用后端登出 API，清除服务端 Session
      await logoutApi();
    } catch (error) {
      // 忽略登出 API 错误，继续执行前端清理
      console.error('Logout error:', error);
    } finally {
      // 清空用户状态
      setUser(null);
      // 跳转到登录页
      navigate('/login');
    }
  }, [navigate]);

  // ========== 上下文值 ==========

  /**
   * 传递给消费者的上下文值
   *
   * 技术要点：
   * - isAdmin 派生自 user.is_superuser
   */
  const value: AuthContextType = {
    user,
    loading,
    login,
    register,
    logout,
    isAdmin: user?.is_superuser || false,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

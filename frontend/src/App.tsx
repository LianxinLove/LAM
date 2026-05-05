/**
 * 应用根组件
 *
 * 功能说明：
 * 1. 配置路由系统
 * 2. 配置国际化（中文）
 * 3. 配置全局认证上下文
 * 4. 配置主题上下文
 * 5. 设置路由保护（登录验证、管理员权限验证）
 *
 * 技术要点：
 * - 使用 React Router v6 实现单页应用路由
 * - 使用 Ant Design ConfigProvider 提供全局配置和主题
 * - 使用 Context API 实现全局状态管理
 *
 * 路由结构：
 * /login              - 登录页（公开访问）
 * /*                 - 受保护的路由（需要登录）
 *   /dashboard       - 仪表盘
 *   /assets          - 资产管理
 *   /consumables     - 耗材管理
 *   /purchases       - 采购管理
 *   /borrows         - 资产借用
 *   /picks           - 耗材领用
 *   /transfers       - 资产调拨
 *   /applications    - 资产业务申请
 *   /logs            - 操作日志（仅管理员）
 *   /statistics      - 统计分析
 *   /categories      - 资产类别（仅管理员）
 *   /suppliers       - 供应商管理（仅管理员）
 *   /help            - 帮助文档
 */

import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ConfigProvider, theme as antdTheme } from "antd";
import zhCN from "antd/locale/zh_CN";
import { AuthProvider } from "./contexts/AuthContext";
import { ThemeProvider, useTheme } from "./contexts/ThemeContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import MainLayout from "./components/Layout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Assets from "./pages/Assets";
import Consumables from "./pages/Consumables";
import Purchases from "./pages/Purchases";
import Borrows from "./pages/Borrows";
import Picks from "./pages/Picks";
import Transfers from "./pages/Transfers";
import AssetApplications from "./pages/AssetApplications";
import Statistics from "./pages/Statistics";
import Logs from "./pages/Logs";
import Categories from "./pages/Categories";
import Suppliers from "./pages/Suppliers";
import Help from "./pages/Help";

/**
 * AppContent 组件
 *
 * 使用 useTheme Hook 获取当前主题，并传递给 ConfigProvider
 *
 * 组件层级结构：
 * ConfigProvider (Ant Design 全局配置和主题)
 *   └── BrowserRouter (路由上下文)
 *       └── AuthProvider (认证上下文)
 *           └── Routes (路由配置)
 *               ├── 登录路由（公开）
 *               └── 受保护路由组
 *                   └── MainLayout (主布局)
 *                       └── 各页面组件
 */
const AppContent: React.FC = () => {
  const { theme } = useTheme();

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: theme === 'dark' ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* 登录路由 - 公开访问 */}
            <Route path="/login" element={<Login />} />

            {/* 受保护路由组 */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <MainLayout />
                </ProtectedRoute>
              }
            >
              {/* 根路径重定向 */}
              <Route index element={<Navigate to="/dashboard" replace />} />

              {/* 基础功能路由 - 所有用户可访问 */}
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="assets" element={<Assets />} />
              <Route path="consumables" element={<Consumables />} />
              <Route path="purchases" element={<Purchases />} />
              <Route path="borrows" element={<Borrows />} />
              <Route path="picks" element={<Picks />} />
              <Route path="transfers" element={<Transfers />} />
              <Route path="applications" element={<AssetApplications />} />
              <Route path="statistics" element={<Statistics />} />
              <Route path="help" element={<Help />} />

              {/* 管理员功能路由 - 仅管理员可访问 */}
              <Route
                path="logs"
                element={
                  <ProtectedRoute adminOnly>
                    <Logs />
                  </ProtectedRoute>
                }
              />
              <Route
                path="categories"
                element={
                  <ProtectedRoute adminOnly>
                    <Categories />
                  </ProtectedRoute>
                }
              />
              <Route
                path="suppliers"
                element={
                  <ProtectedRoute adminOnly>
                    <Suppliers />
                  </ProtectedRoute>
                }
              />
            </Route>
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </ConfigProvider>
  );
};

/**
 * App 组件
 *
 * @returns React 应用根节点
 *
 * 组件层级结构：
 * ThemeProvider (主题上下文)
 *   └── AppContent (包含 ConfigProvider、路由和认证)
 */
const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
};

export default App;

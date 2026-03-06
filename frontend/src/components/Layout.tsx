import React, { useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, Button, message } from 'antd';
import type { MenuProps } from 'antd';
import {
  DashboardOutlined,
  AppstoreOutlined,
  ShoppingOutlined,
  SwapOutlined,
  InboxOutlined,
  FileTextOutlined,
  BarChartOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  QuestionCircleOutlined,
  HistoryOutlined,
  SunOutlined,
  MoonOutlined,
  ToolOutlined,
} from '@ant-design/icons';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import '../styles/Layout.scss';

const { Header, Sider, Content } = Layout;

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, isAdmin } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const handleLogout = () => {
    logout();
    message.success('已退出登录');
    navigate('/login');
  };

  const menuItems: MenuProps['items'] = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/assets',
      icon: <AppstoreOutlined />,
      label: '资产管理',
    },
    {
      key: '/consumables',
      icon: <InboxOutlined />,
      label: '耗材管理',
    },
    {
      key: '/purchases',
      icon: <ShoppingOutlined />,
      label: '采购管理',
    },
    {
      key: '/borrows',
      icon: <SwapOutlined />,
      label: '资产借用',
    },
    {
      key: '/picks',
      icon: <FileTextOutlined />,
      label: '耗材领用',
    },
    {
      key: '/transfers',
      icon: <SwapOutlined />,
      label: '资产转移',
    },
    {
      key: '/applications',
      icon: <ToolOutlined />,
      label: '资产业务',
    },
    ...(isAdmin ? [
      {
        key: '/logs',
        icon: <HistoryOutlined />,
        label: '操作日志',
      },
    ] : []),
    {
      key: '/statistics',
      icon: <BarChartOutlined />,
      label: '统计分析',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '基础数据',
      children: [
        ...(isAdmin ? [
          {
            key: '/categories',
            label: '资产类别',
          },
          {
            key: '/suppliers',
            label: '供应商管理',
          },
        ] : []),
      ],
    },
    {
      key: '/help',
      icon: <QuestionCircleOutlined />,
      label: '帮助文档',
    },
  ];

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人信息',
      onClick: () => message.info('个人信息功能开发中'),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ];

  return (
    <Layout className="layout-container">
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#001529',
          color: '#fff',
          fontSize: collapsed ? '16px' : '18px',
          fontWeight: 'bold',
          padding: collapsed ? '0' : '0 16px',
          overflow: 'hidden',
          whiteSpace: 'nowrap'
        }}>
          {collapsed ? 'LAM' : '资产管理系统'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header className="layout-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{ fontSize: '16px', width: 64, height: 64 }}
          />
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <Button
              type="text"
              icon={theme === 'dark' ? <SunOutlined /> : <MoonOutlined />}
              onClick={toggleTheme}
              style={{ fontSize: '16px', width: 48, height: 48 }}
              title={theme === 'dark' ? '切换到亮色主题' : '切换到暗色主题'}
            />
            <span style={{ color: theme === 'dark' ? 'var(--text-secondary)' : '#666' }}>
              欢迎, {user?.username}
              {isAdmin && <span style={{ marginLeft: 8, color: '#1890ff' }}>(管理员)</span>}
            </span>
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <Avatar icon={<UserOutlined />} style={{ cursor: 'pointer', backgroundColor: '#1890ff' }} />
            </Dropdown>
          </div>
        </Header>
        <Content style={{ margin: '24px', overflow: 'auto' }}>
          <div className="layout-content">
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;

import React, { useState } from 'react';
import { Form, Input, Button, Card, Tabs, Row, Col } from 'antd';
import type { TabsProps } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, ExperimentOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import type { LoginRequest, RegisterRequest } from '../types';
import '../styles/Login.scss';

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const { login: authLogin, register: authRegister } = useAuth();

  const handleLogin = async (values: LoginRequest) => {
    setLoading(true);
    try {
      await authLogin(values);
    } catch (error: any) {
      // AuthContext already handles error messages
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (values: RegisterRequest) => {
    setLoading(true);
    try {
      await authRegister(values);
    } catch (error: any) {
      // AuthContext already handles error messages
    } finally {
      setLoading(false);
    }
  };

  const tabItems: TabsProps['items'] = [
    {
      key: 'login',
      label: '登录',
      children: (
        <Form
          name="login"
          onFinish={handleLogin}
          autoComplete="off"
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="username"
            // rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input 
              prefix={<UserOutlined style={{ color: '#1890ff' }} />} 
              placeholder="请输入用户名" 
              style={{ borderRadius: '8px' }}
            />
          </Form.Item>
          <Form.Item
            name="password"
            // rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password 
              prefix={<LockOutlined style={{ color: '#1890ff' }} />} 
              placeholder="请输入密码"
              style={{ borderRadius: '8px' }}
            />
          </Form.Item>
          <Form.Item style={{ marginBottom: '8px' }}>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading} 
              block 
              size="large"
              style={{ 
                height: '48px',
                fontSize: '16px',
                fontWeight: '500',
                borderRadius: '8px'
              }}
            >
              登录
            </Button>
          </Form.Item>
        </Form>
      ),
    },
    {
      key: 'register',
      label: '注册',
      children: (
        <Form
          name="register"
          onFinish={handleRegister}
          autoComplete="off"
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="username"
            // rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input 
              prefix={<UserOutlined style={{ color: '#1890ff' }} />} 
              placeholder="请输入用户名"
              style={{ borderRadius: '8px' }}
            />
          </Form.Item>
          <Form.Item
            name="email"
          >
            <Input 
              prefix={<MailOutlined style={{ color: '#1890ff' }} />} 
              placeholder="请输入邮箱（可选）"
              style={{ borderRadius: '8px' }}
            />
          </Form.Item>
          <Form.Item
            name="password"
            // rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password 
              prefix={<LockOutlined style={{ color: '#1890ff' }} />} 
              placeholder="请输入密码"
              style={{ borderRadius: '8px' }}
            />
          </Form.Item>
          <Form.Item
            name="confirm"
            dependencies={['password']}
            // rules={[
            //   { required: true, message: '请确认密码' },
            //   ({ getFieldValue }) => ({
            //     validator(_, value) {
            //       if (!value || getFieldValue('password') === value) {
            //         return Promise.resolve();
            //       }
            //       return Promise.reject(new Error('两次输入的密码不一致'));
            //     },
            //   }),
            // ]}
          >
            <Input.Password 
              prefix={<LockOutlined style={{ color: '#1890ff' }} />} 
              placeholder="请确认密码"
              style={{ borderRadius: '8px' }}
            />
          </Form.Item>
          <Form.Item style={{ marginBottom: '8px' }}>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading} 
              block 
              size="large"
              style={{ 
                height: '48px',
                fontSize: '16px',
                fontWeight: '500',
                borderRadius: '8px'
              }}
            >
              注册
            </Button>
          </Form.Item>
        </Form>
      ),
    },
  ];

  return (
    <div className="login-container">
      <Row gutter={[32, 0]} style={{ width: '100%', maxWidth: '1200px' }}>
        <Col xs={0} sm={0} md={12} lg={12} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{
            color: '#fff',
            textAlign: 'center',
            padding: '40px'
          }}>
            <ExperimentOutlined style={{ fontSize: '120px', marginBottom: '24px' }} />
            <h1 style={{ 
              fontSize: '48px', 
              fontWeight: 'bold', 
              marginBottom: '16px',
              color: '#fff'
            }}>
              课题组资产管理系统
            </h1>
            <p style={{ 
              fontSize: '18px', 
              opacity: 0.9,
              lineHeight: '1.6'
            }}>
              高效管理科研资产，提升实验室运营效率
            </p>
            <div style={{ marginTop: '32px', fontSize: '16px', opacity: 0.8 }}>
              <p>✓ 资产全生命周期管理</p>
              <p>✓ 智能库存预警</p>
              <p>✓ 规范化审批流程</p>
              <p>✓ 数据统计分析</p>
            </div>
          </div>
        </Col>
        <Col xs={24} sm={24} md={12} lg={12} style={{ display: 'flex', alignItems: 'center' }}>
          <Card
            className="login-card"
            bordered={false}
          >
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
              <h2 style={{ fontSize: '28px', fontWeight: 'bold', margin: 0 }}>
                欢迎使用
              </h2>
              <p style={{ color: '#666', marginTop: '8px', margin: 0 }}>
                请登录或注册以继续
              </p>
            </div>
            <Tabs
              defaultActiveKey="login"
              centered
              size="large"
              items={tabItems}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Login;

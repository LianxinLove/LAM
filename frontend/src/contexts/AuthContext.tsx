import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { message } from 'antd';
import { login as loginApi, register as registerApi, logout as logoutApi, getCurrentUser } from '../api/auth';
import type { User, LoginRequest, RegisterRequest } from '../types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      getCurrentUser()
        .then((response) => {
          if (response.success) {
            setUser(response.data);
          } else {
            localStorage.removeItem('token');
          }
        })
        .catch(() => {
          localStorage.removeItem('token');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (credentials: LoginRequest) => {
    try {
      const response = await loginApi(credentials);
      if (response.success) {
        localStorage.setItem('token', response.data.token);
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
      message.error(error.response?.data?.message || '登录失败');
    }
  };

  const register = async (data: RegisterRequest) => {
    try {
      const response = await registerApi(data);
      if (response.success) {
        localStorage.setItem('token', response.data.token);
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
      message.error(error.response?.data?.message || '注册失败');
    }
  };

  const logout = async () => {
    try {
      await logoutApi();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      setUser(null);
      navigate('/login');
    }
  };

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

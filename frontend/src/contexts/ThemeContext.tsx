/**
 * 主题上下文模块
 *
 * 功能说明：
 * 1. 管理应用主题状态（亮色/暗色）
 * 2. 提供主题切换方法
 * 3. 使用 localStorage 持久化用户选择
 * 4. 应用初始化时自动恢复主题设置
 *
 * 技术要点：
 * - 使用 React Context API 实现全局状态共享
 * - 主题偏好存储在 localStorage 中
 * - 支持 'light' 和 'dark' 两种主题
 *
 * 使用方式：
 * ```tsx
 * // 在组件中使用 Hook
 * const { theme, toggleTheme } = useTheme();
 *
 * // 在应用根组件包裹 ThemeProvider
 * <ThemeProvider><App /></ThemeProvider>
 * ```
 */

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';

/**
 * 主题类型定义
 */
export type ThemeMode = 'light' | 'dark';

/**
 * 主题上下文类型定义
 */
interface ThemeContextType {
  /** 当前主题模式 */
  theme: ThemeMode;
  /** 切换主题方法 */
  toggleTheme: () => void;
  /** 设置指定主题 */
  setTheme: (theme: ThemeMode) => void;
}

/**
 * localStorage 存储键名
 */
const THEME_STORAGE_KEY = 'app-theme';

/**
 * 创建主题上下文
 */
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

/**
 * useTheme Hook
 *
 * 功能：在组件中访问主题上下文
 *
 * @throws {Error} 如果在 ThemeProvider 外部使用
 * @returns {ThemeContextType} 主题上下文值
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { theme, toggleTheme } = useTheme();
 *   return <button onClick={toggleTheme}>当前主题: {theme}</button>;
 * }
 * ```
 */
export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

/**
 * ThemeProvider 组件属性类型
 */
interface ThemeProviderProps {
  children: ReactNode;
}

/**
 * 从 localStorage 读取保存的主题
 */
const getStoredTheme = (): ThemeMode => {
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === 'light' || stored === 'dark') {
      return stored;
    }
  } catch (error) {
    console.error('Error reading theme from localStorage:', error);
  }
  // 默认返回亮色主题
  return 'light';
};

/**
 * 主题保存到 localStorage
 */
const storeTheme = (theme: ThemeMode) => {
  try {
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  } catch (error) {
    console.error('Error saving theme to localStorage:', error);
  }
};

/**
 * ThemeProvider 组件
 *
 * 功能：
 * 1. 封装主题状态和逻辑
 * 2. 应用初始化时从 localStorage 恢复主题设置
 * 3. 更新主题时同步更新 data-theme 属性
 * 4. 提供主题切换方法给子组件
 *
 * @example
 * ```tsx
 * <ThemeProvider>
 *   <App />
 * </ThemeProvider>
 * ```
 */
export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  // ========== 状态管理 ==========

  /** 当前主题模式，初始值从 localStorage 读取 */
  const [theme, setThemeState] = useState<ThemeMode>(getStoredTheme);

  // ========== 副作用：初始化和同步 ==========

  /**
   * 组件挂载时设置 data-theme 属性
   * 主题变化时同步更新 data-theme 属性
   */
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  /**
   * 检测系统主题偏好（可选功能）
   * 当用户没有手动设置过主题时，可以跟随系统主题
   */
  useEffect(() => {
    // 仅在 localStorage 没有值时监听系统主题变化
    const hasStoredTheme = localStorage.getItem(THEME_STORAGE_KEY) !== null;
    if (hasStoredTheme) return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleChange = (e: MediaQueryListEvent) => {
      setThemeState(e.matches ? 'dark' : 'light');
    };

    // 初始设置
    setThemeState(mediaQuery.matches ? 'dark' : 'light');

    // 监听系统主题变化
    mediaQuery.addEventListener('change', handleChange);

    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);

  // ========== 主题方法 ==========

  /**
   * 切换主题
   *
   * 流程：
   * 1. 在 light 和 dark 之间切换
   * 2. 更新状态
   * 3. 保存到 localStorage
   */
  const toggleTheme = useCallback(() => {
    setThemeState((prevTheme) => {
      const newTheme: ThemeMode = prevTheme === 'light' ? 'dark' : 'light';
      storeTheme(newTheme);
      return newTheme;
    });
  }, []);

  /**
   * 设置指定主题
   *
   * @param newTheme - 要设置的主题
   */
  const setTheme = useCallback((newTheme: ThemeMode) => {
    setThemeState(newTheme);
    storeTheme(newTheme);
  }, []);

  // ========== 上下文值 ==========

  const value: ThemeContextType = {
    theme,
    toggleTheme,
    setTheme,
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

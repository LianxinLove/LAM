import React from 'react';

interface EmptyStateProps {
  icon: React.ReactNode;
  message: string;
  hint?: string;
}

/**
 * 空状态组件
 * 用于显示数据为空时的提示信息
 */
export const EmptyState: React.FC<EmptyStateProps> = ({ icon, message, hint }) => {
  return (
    <div style={{ textAlign: 'center', padding: '60px 0', color: '#8c8c8c' }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>{icon}</div>
      <p>{message}</p>
      {hint && <p style={{ fontSize: 12 }}>{hint}</p>}
    </div>
  );
};

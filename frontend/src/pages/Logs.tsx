import React, { useEffect, useState } from 'react';
import { Table, Tag, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { getLogs } from '../api/logs';
import type { OperationLog } from '../types';
import '../styles/common.scss';

// 操作日志页面组件（仅管理员可见）
const Logs: React.FC = () => {
  const [logs, setLogs] = useState<OperationLog[]>([]);
  const [loading, setLoading] = useState(false);

  // 初始化加载操作日志
  useEffect(() => {
    fetchLogs();
  }, []);

  // 获取操作日志列表
  const fetchLogs = async () => {
    setLoading(true);
    try {
      const response = await getLogs();
      setLogs(response.data.items || []);
    } catch (error) {
      message.error('获取操作日志失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取操作类型颜色
  const getActionColor = (action: string) => {
    const colors: Record<string, string> = {
      create: 'green',
      update: 'blue',
      delete: 'red',
      approve: 'green',
      reject: 'orange',
      borrow: 'blue',
      return: 'green',
      pick: 'blue',
      transfer: 'purple',
    };
    return colors[action] || 'default';
  };

  // 表格列定义
  const columns: ColumnsType<OperationLog> = [
    {
      title: '操作人',
      dataIndex: ['user', 'username'],
      key: 'user',
    },
    {
      title: '操作类型',
      dataIndex: 'action',
      key: 'action',
      render: (action: string) => (
        <Tag color={getActionColor(action)}>{action}</Tag>
      ),
    },
    {
      title: '操作对象',
      dataIndex: 'model',
      key: 'model',
    },
    {
      title: '对象ID',
      dataIndex: 'object_id',
      key: 'object_id',
    },
    {
      title: '对象表示',
      dataIndex: 'object_repr',
      key: 'object_repr',
    },
    {
      title: '操作详情',
      dataIndex: 'details',
      key: 'details',
      render: (details?: string) => details || '-',
    },
    {
      title: '操作时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (timestamp: string) => new Date(timestamp).toLocaleString('zh-CN'),
    },
  ];

  return (
    <div>
      <h2 className="page-title" style={{ marginBottom: 16 }}>操作日志</h2>
      <div className="table-container">
        <Table
          columns={columns}
          dataSource={logs}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </div>
    </div>
  );
};

export default Logs;

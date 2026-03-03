import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Table, Tag, Alert, Spin } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  AppstoreOutlined,
  InboxOutlined,
  SwapOutlined,
  ShoppingOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { getDashboardData } from '../api/dashboard';
import { useAuth } from '../contexts/AuthContext';
import type { DashboardData, Consumable } from '../types';
import '../styles/common.scss';

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const { isAdmin } = useAuth();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await getDashboardData();
      setData(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  const lowStockColumns: ColumnsType<Consumable> = [
    {
      title: '耗材名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '当前库存',
      dataIndex: 'stock',
      key: 'stock',
      render: (stock: number, record: Consumable) => (
        <Tag color="red">{stock} {record.unit}</Tag>
      ),
    },
    {
      title: '最低库存',
      dataIndex: 'min_stock',
      key: 'min_stock',
    },
  ];

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>仪表盘</h2>
      
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="资产总数"
              value={data?.asset_count || 0}
              prefix={<AppstoreOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="耗材总数"
              value={data?.consumable_count || 0}
              prefix={<InboxOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="我的借用中"
              value={data?.my_borrows || 0}
              prefix={<SwapOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="我的采购申请"
              value={data?.my_requests || 0}
              prefix={<ShoppingOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {isAdmin && (
        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} sm={12} lg={8}>
            <Card>
              <Statistic
                title="待审批采购"
                value={data?.pending_purchases || 0}
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: '#fa8c16' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={8}>
            <Card>
              <Statistic
                title="待审批转移"
                value={data?.pending_transfers || 0}
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: '#fa8c16' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={8}>
            <Card>
              <Statistic
                title="待审批领料"
                value={data?.pending_picks || 0}
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: '#fa8c16' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {data?.low_stock_items && data.low_stock_items.length > 0 && (
        <Card
          title={
            <span>
              <WarningOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />
              低库存预警
            </span>
          }
          style={{ marginTop: 24 }}
        >
          <Alert
            message="以下耗材库存已低于最低库存，请及时补充"
            type="warning"
            showIcon
            style={{ marginBottom: 16 }}
          />
          <Table
            dataSource={data.low_stock_items}
            columns={lowStockColumns}
            rowKey="id"
            pagination={false}
            size="small"
          />
        </Card>
      )}

      {data?.low_stock_items && data.low_stock_items.length === 0 && (
        <Card style={{ marginTop: 24 }}>
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <CheckCircleOutlined style={{ fontSize: 48, color: '#52c41a' }} />
            <p style={{ marginTop: 16, color: '#52c41a', fontSize: 16 }}>
              所有耗材库存充足
            </p>
          </div>
        </Card>
      )}
    </div>
  );
};

export default Dashboard;

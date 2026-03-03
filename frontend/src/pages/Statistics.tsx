import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Table, Spin, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  AppstoreOutlined,
  InboxOutlined,
  DollarOutlined,
  WarningOutlined,
  ShoppingOutlined,
  SwapOutlined
} from '@ant-design/icons';
import { getStatisticsData } from '../api/statistics';
import type { StatisticsData } from '../types';
import '../styles/common.scss';

// 统计分析页面组件
const Statistics: React.FC = () => {
  const [data, setData] = useState<StatisticsData | null>(null);
  const [loading, setLoading] = useState(true);

  // 初始化加载统计数据
  useEffect(() => {
    fetchStatistics();
  }, []);

  // 获取统计数据
  const fetchStatistics = async () => {
    try {
      const response = await getStatisticsData();
      setData(response.data);
    } catch (error) {
      message.error('获取统计数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载状态显示
  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  // 资产状态表格列定义
  const assetStatusColumns: ColumnsType<{ status: string; count: number }> = [
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const texts: Record<string, string> = {
          available: '可用',
          in_use: '使用中',
          maintenance: '维修中',
          retired: '已报废',
        };
        return texts[status] || status;
      },
    },
    {
      title: '数量',
      dataIndex: 'count',
      key: 'count',
    },
  ];

  // 资产类别表格列定义
  const assetCategoryColumns: ColumnsType<{ category: string; count: number }> = [
    {
      title: '类别',
      dataIndex: 'category',
      key: 'category',
    },
    {
      title: '数量',
      dataIndex: 'count',
      key: 'count',
    },
  ];

  // 采购状态表格列定义
  const purchaseStatusColumns: ColumnsType<{ status: string; count: number }> = [
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const texts: Record<string, string> = {
          pending: '待审批',
          approved: '已审批',
          purchased: '已采购',
          rejected: '已拒绝',
        };
        return texts[status] || status;
      },
    },
    {
      title: '数量',
      dataIndex: 'count',
      key: 'count',
    },
  ];

  return (
    <div>
      <h2 className="page-title" style={{ marginBottom: 24 }}>统计分析</h2>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card className="stat-card">
            <Statistic
              title="耗材总价值"
              value={data?.total_consumable_value || 0}
              prefix={<DollarOutlined />}
              precision={2}
              valueStyle={{ color: '#1890ff' }}
              suffix="元"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="stat-card">
            <Statistic
              title="低库存耗材数量"
              value={data?.low_stock_count || 0}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="stat-card">
            <Statistic
              title="采购总预算"
              value={data?.total_budget || 0}
              prefix={<ShoppingOutlined />}
              precision={2}
              valueStyle={{ color: '#52c41a' }}
              suffix="元"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="stat-card">
            <Statistic
              title="当前借用中数量"
              value={data?.active_borrows || 0}
              prefix={<SwapOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="资产按状态统计">
            <Table
              dataSource={data?.asset_by_status || []}
              columns={assetStatusColumns}
              rowKey="status"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="资产按类别统计">
            <Table
              dataSource={data?.asset_by_category || []}
              columns={assetCategoryColumns}
              rowKey="category"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card title="采购申请按状态统计">
            <Table
              dataSource={data?.purchase_by_status || []}
              columns={purchaseStatusColumns}
              rowKey="status"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="资产概览">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Statistic
                  title="资产总数"
                  value={data?.asset_by_status?.reduce((sum, item) => sum + item.count, 0) || 0}
                  prefix={<AppstoreOutlined />}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="耗材总数"
                  value={data?.asset_by_category?.reduce((sum, item) => sum + item.count, 0) || 0}
                  prefix={<InboxOutlined />}
                />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Statistics;

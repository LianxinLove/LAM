import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Card, Row, Col, Statistic, Table, Spin, message, Progress } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  AppstoreOutlined,
  InboxOutlined,
  DollarOutlined,
  WarningOutlined,
  ShoppingOutlined,
  SwapOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { Column, Pie, Gauge } from '@ant-design/charts';
import { getStatisticsData } from '../api/statistics';
import type { StatisticsData } from '../types';
import { ASSET_STATUS_TEXTS, PURCHASE_STATUS_TEXTS, getAssetStatusText, getPurchaseStatusText } from '../constants/statusConstants';
import { getHealthStatus, calculateHealthScore, CHART_COLORS } from '../constants/colors';
import { EmptyState } from '../components/EmptyState';
import '../styles/common.scss';

// 表格列定义（移到组件外部，避免每次渲染重建）
const assetStatusColumns: ColumnsType<{ status: string; count: number }> = [
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    render: (status: string) => getAssetStatusText(status),
  },
  {
    title: '数量',
    dataIndex: 'count',
    key: 'count',
  },
];

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

const purchaseStatusColumns: ColumnsType<{ status: string; count: number }> = [
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    render: (status: string) => getPurchaseStatusText(status),
  },
  {
    title: '数量',
    dataIndex: 'count',
    key: 'count',
  },
];

const Statistics: React.FC = () => {
  const [data, setData] = useState<StatisticsData | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStatistics = useCallback(async () => {
    try {
      const response = await getStatisticsData();
      setData(response.data);
    } catch (error) {
      message.error('获取统计数据失败');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatistics();
  }, [fetchStatistics]);

  // 使用 useMemo 优化数据转换
  const assetCategoryData = useMemo(() =>
    data?.asset_by_category?.map(item => ({
      category: item.category,
      count: item.count,
    })) || [],
    [data?.asset_by_category]
  );

  const purchaseStatusData = useMemo(() =>
    data?.purchase_by_status?.map(item => ({
      status: getPurchaseStatusText(item.status),
      count: item.count,
    })) || [],
    [data?.purchase_by_status]
  );

  // 使用 useMemo 优化健康指标计算
  const healthMetrics = useMemo(() => {
    const lowStockCount = data?.low_stock_count || 0;
    const healthScore = calculateHealthScore(lowStockCount);
    const healthStatus = getHealthStatus(healthScore);
    return {
      healthScore,
      ...healthStatus,
    };
  }, [data?.low_stock_count]);

  // 使用 useMemo 优化图表配置
  const categoryChartConfig = useMemo(() => ({
    data: assetCategoryData,
    xField: 'category',
    yField: 'count',
    label: {
      position: 'top' as const,
      style: { fill: '#000' },
    },
    color: CHART_COLORS.PRIMARY,
    columnStyle: { radius: [4, 4, 0, 0] },
    xAxis: { label: { autoRotate: true, autoHide: true } },
    height: 300,
  }), [assetCategoryData]);

  const statusChartConfig = useMemo(() => ({
    data: purchaseStatusData,
    angleField: 'count',
    colorField: 'status',
    radius: 0.8,
    innerRadius: 0.6,
    label: {
      type: 'inner' as const,
      offset: '-50%',
      content: '{value}',
      style: { textAlign: 'center' as const, fontSize: 14, fill: '#fff' },
    },
    legend: { position: 'bottom' as const },
    color: CHART_COLORS.STATUS_COLORS,
    height: 300,
  }), [purchaseStatusData]);

  const gaugeChartConfig = useMemo(() => ({
    percent: healthMetrics.healthScore / 100,
    range: { color: healthMetrics.color },
    indicator: {
      pointer: { style: { display: 'none' } },
      pin: { style: { display: 'none' } },
    },
    statistic: {
      title: { content: '库存健康度', style: { fontSize: 16 } },
      content: {
        style: { fontSize: 32, fontWeight: 'bold', color: healthMetrics.color },
        formatter: () => `${healthMetrics.healthScore}%`,
      },
    },
    height: 200,
  }), [healthMetrics]);

  // 计算财务指标
  const financialMetrics = useMemo(() => {
    const totalValue = data?.total_consumable_value || 0;
    const totalBudget = data?.total_budget || 0;
    return {
      totalValue,
      totalBudget,
      budgetExecutionRate: totalBudget > 0 ? ((totalValue / totalBudget) * 100).toFixed(1) : '0',
      totalAssetValue: (totalValue + totalBudget).toFixed(2),
    };
  }, [data?.total_consumable_value, data?.total_budget]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <h2 className="page-title" style={{ marginBottom: 24 }}>统计分析</h2>

      {/* 顶部统计卡片 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card className="stat-card">
            <Statistic
              title="耗材总价值"
              value={financialMetrics.totalValue}
              prefix={<DollarOutlined />}
              precision={2}
              valueStyle={{ color: CHART_COLORS.PRIMARY }}
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
              valueStyle={{ color: CHART_COLORS.ERROR }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="stat-card">
            <Statistic
              title="采购总预算"
              value={financialMetrics.totalBudget}
              prefix={<ShoppingOutlined />}
              precision={2}
              valueStyle={{ color: CHART_COLORS.SUCCESS }}
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
              valueStyle={{ color: CHART_COLORS.WARNING }}
            />
          </Card>
        </Col>
      </Row>

      {/* 价值统计图表区域 */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="财务概览">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <div style={{ marginBottom: 16 }}>
                  <div style={{ color: '#8c8c8c', marginBottom: 8 }}>耗材总价值</div>
                  <Progress
                    type="circle"
                    percent={Math.min(100, Math.round(financialMetrics.totalValue / 1000))}
                    format={() => `¥${(financialMetrics.totalValue / 1000).toFixed(1)}k`}
                    strokeColor={CHART_COLORS.PRIMARY}
                    size={100}
                  />
                </div>
              </Col>
              <Col span={12}>
                <div style={{ marginBottom: 16 }}>
                  <div style={{ color: '#8c8c8c', marginBottom: 8 }}>采购总预算</div>
                  <Progress
                    type="circle"
                    percent={Math.min(100, Math.round(financialMetrics.totalBudget / 1000))}
                    format={() => `¥${(financialMetrics.totalBudget / 1000).toFixed(1)}k`}
                    strokeColor={CHART_COLORS.SUCCESS}
                    size={100}
                  />
                </div>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <div style={{ padding: '12px 0' }}>
                  <CheckCircleOutlined style={{ color: CHART_COLORS.SUCCESS, marginRight: 8, fontSize: 18 }} />
                  <span>预算执行率：</span>
                  <strong style={{ fontSize: 18, marginLeft: 8 }}>
                    {financialMetrics.budgetExecutionRate}%
                  </strong>
                </div>
              </Col>
              <Col span={12}>
                <div style={{ padding: '12px 0' }}>
                  <DollarOutlined style={{ color: CHART_COLORS.PRIMARY, marginRight: 8, fontSize: 18 }} />
                  <span>总资产价值：</span>
                  <strong style={{ fontSize: 18, marginLeft: 8 }}>
                    ¥{financialMetrics.totalAssetValue}
                  </strong>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 库存健康度仪表盘 */}
        <Col xs={24} lg={12}>
          <Card title={`库存健康度：${healthMetrics.text}`} extra={<span style={{ color: healthMetrics.color, fontWeight: 'bold' }}>{healthMetrics.text}</span>}>
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 250 }}>
              <Gauge {...gaugeChartConfig} />
            </div>
            <div style={{ textAlign: 'center', marginTop: 16, color: '#8c8c8c' }}>
              {healthMetrics.message}
            </div>
          </Card>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        {/* 资产类别分布柱状图 */}
        <Col xs={24} lg={12}>
          <Card title="资产按类别分布" extra={<AppstoreOutlined />}>
            {assetCategoryData.length > 0 ? (
              <Column {...categoryChartConfig} />
            ) : (
              <EmptyState icon={<InboxOutlined />} message="暂无资产数据" />
            )}
          </Card>
        </Col>

        {/* 采购状态分布环形图 */}
        <Col xs={24} lg={12}>
          <Card title="采购申请状态分布" extra={<ShoppingOutlined />}>
            {purchaseStatusData.length > 0 ? (
              <Pie {...statusChartConfig} />
            ) : (
              <EmptyState
                icon={<ShoppingOutlined />}
                message="暂无采购申请数据"
                hint="请先在'采购管理'中创建采购申请"
              />
            )}
          </Card>
        </Col>
      </Row>

      {/* 表格区域 */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="资产按状态统计（表格）">
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

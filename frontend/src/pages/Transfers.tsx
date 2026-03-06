import React, { useEffect, useState } from 'react';
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Select,
  message,
  Tag,
  Card,
  Row,
  Col,
  Tabs
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import type { TabsProps } from 'antd';
import {
  PlusOutlined,
  CheckOutlined,
  CloseOutlined,
  EyeOutlined
} from '@ant-design/icons';
import { getTransfers, createTransfer, approveTransfer, rejectTransfer } from '../api/transfers';
import { getAssets } from '../api/assets';
import { useAuth } from '../contexts/AuthContext';
import type { TransferRequest, AssetLite, QueryParams } from '../types';
import '../styles/common.scss';

const { Option } = Select;
const { TextArea } = Input;

// 资产转移页面组件
const Transfers: React.FC = () => {
  const [requests, setRequests] = useState<TransferRequest[]>([]);
  const [assets, setAssets] = useState<AssetLite[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [viewModalVisible, setViewModalVisible] = useState(false);
  const [viewingRequest, setViewingRequest] = useState<TransferRequest | null>(null);
  const [activeTab, setActiveTab] = useState('my');
  const [selectedAsset, setSelectedAsset] = useState<AssetLite | null>(null);
  const [form] = Form.useForm<any>();
  const { isAdmin } = useAuth();

  // 初始化加载数据
  useEffect(() => {
    fetchRequests();
    fetchAssets();
  }, [activeTab]);

  // 获取转移申请列表
  const fetchRequests = async () => {
    setLoading(true);
    try {
      // "我的申请" tab: 显示当前用户的所有申请
      // "调拨审批" tab: 仅显示待审批的申请
      const params: QueryParams = activeTab === 'my' ? { my: true } : { status: 'pending' };
      const response = await getTransfers(params);
      setRequests(response.data.items || []);
    } catch (error) {
      message.error('获取转移申请列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取资产列表
  const fetchAssets = async () => {
    try {
      const response = await getAssets();
      setAssets(response.data.items || []);
    } catch (error) {
      console.error('获取资产列表失败:', error);
    }
  };

  // 打开转移申请弹窗
  const handleAdd = () => {
    form.resetFields();
    setSelectedAsset(null);
    setModalVisible(true);
  };

  // 查看转移申请详情
  const handleView = (record: TransferRequest) => {
    setViewingRequest(record);
    setViewModalVisible(true);
  };

  // 处理资产选择变化
  const handleAssetChange = (value: number) => {
    const asset = assets.find(a => a.id === value);
    setSelectedAsset(asset || null);
  };

  // 提交转移申请
  const handleSubmit = async (values: any) => {
    try {
      await createTransfer(values);
      message.success('转移申请已提交');
      setModalVisible(false);
      fetchRequests();
    } catch (error: any) {
      const errorMsg = error?.message || '提交失败';
      message.error(errorMsg);
    }
  };

  // 审批转移申请
  const handleApprove = async (id: number, action: 'approve' | 'reject') => {
    try {
      if (action === 'approve') {
        await approveTransfer(id);
      } else {
        await rejectTransfer(id, '');
      }
      message.success(action === 'approve' ? '已批准' : '已拒绝');
      fetchRequests();
    } catch (error: any) {
      const errorMsg = error?.message || '操作失败';
      message.error(errorMsg);
    }
  };

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'orange',
      approved: 'green',
      rejected: 'red',
    };
    return colors[status] || 'default';
  };

  // 获取状态文本
  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      pending: '待审批',
      approved: '已批准',
      rejected: '已拒绝',
    };
    return texts[status] || status;
  };

  // 表格列定义
  const columns: ColumnsType<TransferRequest> = [
    {
      title: '资产名称',
      dataIndex: ['asset', 'name'],
      key: 'asset',
    },
    {
      title: '资产编号',
      dataIndex: ['asset', 'lab_asset_code'],
      key: 'asset_code',
    },
    {
      title: '原位置',
      dataIndex: 'from_location',
      key: 'from_location',
    },
    {
      title: '新位置',
      dataIndex: 'to_location',
      key: 'to_location',
    },
    {
      title: '转移原因',
      dataIndex: 'reason',
      key: 'reason',
      render: (reason?: string) => reason || '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>{getStatusText(status)}</Tag>
      ),
    },
    {
      title: '申请人',
      dataIndex: ['applicant', 'username'],
      key: 'applicant',
    },
    {
      title: '申请时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: TransferRequest) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
          >
            查看
          </Button>
          {isAdmin && record.status === 'pending' && (
            <>
              <Button
                type="link"
                icon={<CheckOutlined />}
                onClick={() => handleApprove(record.id, 'approve')}
              >
                批准
              </Button>
              <Button
                type="link"
                danger
                icon={<CloseOutlined />}
                onClick={() => handleApprove(record.id, 'reject')}
              >
                拒绝
              </Button>
            </>
          )}
        </Space>
      ),
    },
  ];

  // 标签页配置
  const tabItems: TabsProps['items'] = [
    {
      key: 'my',
      label: '我的转移申请',
    },
    ...(isAdmin ? [{
      key: 'approve',
      label: '转移审批',
    }] : []),
  ];

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">资产转移</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          提交转移申请
        </Button>
      </div>

      <Tabs
        activeKey={activeTab}
        items={tabItems}
        onChange={(key) => setActiveTab(key)}
      />

      <div className="table-container">
        <Table
          columns={columns}
          dataSource={requests}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </div>

      <Modal
        title="提交转移申请"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="asset_id"
            label="选择资产"
            rules={[{ required: true, message: '请选择资产' }]}
          >
            <Select
              placeholder="请选择资产"
              onChange={handleAssetChange}
              showSearch
              optionFilterProp="children"
            >
              {assets.map(asset => (
                <Option key={asset.id} value={asset.id}>
                  {asset.lab_asset_code} - {asset.name} (当前位置: {asset.location || '未设置'})
                </Option>
              ))}
            </Select>
          </Form.Item>
          {selectedAsset && (
            <Card size="small" style={{ marginBottom: 16 }}>
              <p><strong>当前位置：</strong>{selectedAsset.location || '未设置'}</p>
            </Card>
          )}
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="to_campus"
                label="目标校区"
                rules={[{ required: true, message: '请输入校区' }]}
              >
                <Input placeholder="如：本部" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="to_building"
                label="目标楼宇"
                rules={[{ required: true, message: '请输入楼宇' }]}
              >
                <Input placeholder="如：实验楼A" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="to_room"
                label="目标房间"
              >
                <Input placeholder="如：301" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item
            name="reason"
            label="转移原因"
            rules={[{ required: true, message: '请输入转移原因' }]}
          >
            <TextArea rows={4} placeholder="请输入转移原因" />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                提交
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="转移申请详情"
        open={viewModalVisible}
        onCancel={() => setViewModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setViewModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={600}
      >
        {viewingRequest && (
          <Card>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <strong>资产名称：</strong>{viewingRequest.asset?.name}
              </Col>
              <Col span={12}>
                <strong>资产编号：</strong>{viewingRequest.asset?.lab_asset_code}
              </Col>
              <Col span={12}>
                <strong>原位置：</strong>{viewingRequest.from_location}
              </Col>
              <Col span={12}>
                <strong>新位置：</strong>{viewingRequest.to_location}
              </Col>
              <Col span={12}>
                <strong>状态：</strong>
                <Tag color={getStatusColor(viewingRequest.status)}>
                  {getStatusText(viewingRequest.status)}
                </Tag>
              </Col>
              <Col span={12}>
                <strong>申请人：</strong>{viewingRequest.applicant?.username}
              </Col>
              {viewingRequest.receiver && (
                <Col span={12}>
                  <strong>接收确认人：</strong>{viewingRequest.receiver.username}
                </Col>
              )}
              <Col span={12}>
                <strong>申请时间：</strong>{new Date(viewingRequest.created_at).toLocaleString('zh-CN')}
              </Col>
              {viewingRequest.approver && (
                <Col span={12}>
                  <strong>审批人：</strong>{viewingRequest.approver.username}
                </Col>
              )}
              {viewingRequest.approved_at && (
                <Col span={12}>
                  <strong>审批时间：</strong>{new Date(viewingRequest.approved_at).toLocaleString('zh-CN')}
                </Col>
              )}
              <Col span={24}>
                <strong>转移原因：</strong>{viewingRequest.reason}
              </Col>
            </Row>
          </Card>
        )}
      </Modal>
    </div>
  );
};

export default Transfers;

import React, { useEffect, useState } from 'react';
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Select,
  InputNumber,
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
import { getPurchases, createPurchase, approvePurchase, rejectPurchase } from '../api/purchases';
import { getSuppliers } from '../api/suppliers';
import { useAuth } from '../contexts/AuthContext';
import type { PurchaseRequest, Supplier, PurchaseFormData, QueryParams } from '../types';
import '../styles/common.scss';

const { Option } = Select;
const { TextArea } = Input;

const Purchases: React.FC = () => {
  const [requests, setRequests] = useState<PurchaseRequest[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [viewModalVisible, setViewModalVisible] = useState(false);
  const [viewingRequest, setViewingRequest] = useState<PurchaseRequest | null>(null);
  const [activeTab, setActiveTab] = useState('my');
  const [form] = Form.useForm<PurchaseFormData>();
  const { isAdmin } = useAuth();

  useEffect(() => {
    fetchRequests();
    fetchSuppliers();
  }, [activeTab]);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      // "我的采购申请" tab: 显示当前用户的所有申请
      // "采购审批" tab: 仅显示待审批的申请
      const params: QueryParams = activeTab === 'my' ? { my: true } : { status: 'pending' };
      const response = await getPurchases(params);
      setRequests(response.data.items || []);
    } catch (error) {
      message.error('获取采购申请列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchSuppliers = async () => {
    try {
      const response = await getSuppliers();
      setSuppliers(response.data.items || []);
    } catch (error) {
      console.error('Failed to fetch suppliers:', error);
    }
  };

  const handleAdd = () => {
    form.resetFields();
    setModalVisible(true);
  };

  const handleView = (record: PurchaseRequest) => {
    setViewingRequest(record);
    setViewModalVisible(true);
  };

  const handleSubmit = async (values: PurchaseFormData) => {
    try {
      await createPurchase(values);
      message.success('采购申请已提交');
      setModalVisible(false);
      fetchRequests();
    } catch (error) {
      message.error('提交失败');
    }
  };

  const handleApprove = async (id: number, action: 'approve' | 'reject') => {
    try {
      if (action === 'approve') {
        await approvePurchase(id);
      } else {
        await rejectPurchase(id, '');
      }
      message.success(action === 'approve' ? '已批准' : '已拒绝');
      fetchRequests();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'orange',
      approved: 'green',
      purchased: 'blue',
      rejected: 'red',
    };
    return colors[status] || 'default';
  };

  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      pending: '待审批',
      approved: '已审批',
      purchased: '已采购',
      rejected: '已拒绝',
    };
    return texts[status] || status;
  };

  const columns: ColumnsType<PurchaseRequest> = [
    {
      title: '申请标题',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '物品名称',
      dataIndex: 'item_name',
      key: 'item_name',
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
    },
    {
      title: '预算',
      dataIndex: 'estimated_price',
      key: 'estimated_price',
      render: (price: number) => `¥${price.toFixed(2)}`,
    },
    {
      title: '供应商',
      dataIndex: ['supplier', 'name'],
      key: 'supplier',
      render: (name?: string) => name || '-',
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
      render: (_: any, record: PurchaseRequest) => (
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

  const tabItems: TabsProps['items'] = [
    {
      key: 'my',
      label: '我的采购申请',
    },
    ...(isAdmin ? [{
      key: 'approve',
      label: '采购审批',
    }] : []),
  ];

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">采购管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          提交采购申请
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
        title="提交采购申请"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="title"
            label="采购标题"
            rules={[{ required: true, message: '请输入采购标题' }]}
          >
            <Input placeholder="请输入采购标题" />
          </Form.Item>
          <Form.Item
            name="item_name"
            label="物品名称"
            rules={[{ required: true, message: '请输入物品名称' }]}
          >
            <Input placeholder="请输入物品名称" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="quantity"
                label="数量"
                rules={[{ required: true, message: '请输入数量' }]}
                initialValue={1}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="请输入数量"
                  min={1}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="estimated_price"
                label="预算"
                rules={[{ required: true, message: '请输入预算' }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="请输入预算"
                  min={0}
                  precision={2}
                  prefix="¥"
                />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="supplier_id" label="供应商">
            <Select placeholder="请选择供应商" allowClear>
              {suppliers.map(sup => (
                <Option key={sup.id} value={sup.id}>{sup.name}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="reason"
            label="采购原因"
            rules={[{ required: true, message: '请输入采购原因' }]}
          >
            <TextArea rows={4} placeholder="请输入采购原因" />
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
        title="采购申请详情"
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
                <strong>申请标题：</strong>{viewingRequest.title}
              </Col>
              <Col span={12}>
                <strong>物品名称：</strong>{viewingRequest.item_name}
              </Col>
              <Col span={12}>
                <strong>数量：</strong>{viewingRequest.quantity}
              </Col>
              <Col span={12}>
                <strong>预算：</strong>¥{viewingRequest.estimated_price.toFixed(2)}
              </Col>
              <Col span={12}>
                <strong>供应商：</strong>{viewingRequest.supplier?.name || '-'}
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
                <strong>采购原因：</strong>{viewingRequest.reason}
              </Col>
            </Row>
          </Card>
        )}
      </Modal>
    </div>
  );
};

export default Purchases;

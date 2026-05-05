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
  Tabs,
  Checkbox
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import type { TabsProps } from 'antd';
import {
  PlusOutlined,
  CheckOutlined,
  CloseOutlined,
  EyeOutlined
} from '@ant-design/icons';
import { getPurchases, createPurchase, PurchaseStatusLabel, PurchaseStatusColor } from '../api/purchases';
import { getSuppliers } from '../api/suppliers';
import { useAuth } from '../contexts/AuthContext';
import type { PurchaseRequest, Supplier, PurchaseFormData, QueryParams } from '../types';
import '../styles/common.scss';

const { TextArea } = Input;
const { Option } = Select;

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
    } catch (error: any) {
      const errorMsg = error?.message || '提交失败';
      message.error(errorMsg);
    }
  };

  const handleApprove = async (id: number, action: 'approve' | 'reject', comment?: string) => {
    try {
      const { approvePurchaseRequest, rejectPurchaseRequest } = await import('../api/purchases');
      if (action === 'approve') {
        await approvePurchaseRequest(id, comment);
      } else {
        await rejectPurchaseRequest(id, comment);
      }
      message.success(action === 'approve' ? '已批准' : '已拒绝');
      fetchRequests();
    } catch (error: any) {
      const errorMsg = error?.message || '操作失败';
      message.error(errorMsg);
    }
  };

  const columns: ColumnsType<PurchaseRequest> = [
    {
      title: '序号',
      key: 'index',
      width: 60,
      render: (_: any, __: PurchaseRequest, index: number) => index + 1,
    },
    {
      title: '产品名称',
      dataIndex: 'product_name',
      key: 'product_name',
      width: 150,
    },
    {
      title: '品牌',
      dataIndex: 'brand',
      key: 'brand',
      width: 100,
      render: (brand?: string) => brand || '-',
    },
    {
      title: '货号',
      dataIndex: 'product_code',
      key: 'product_code',
      width: 120,
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 80,
    },
    {
      title: '用途',
      dataIndex: 'purpose',
      key: 'purpose',
      width: 150,
      ellipsis: true,
    },
    {
      title: '申请项目',
      dataIndex: 'project_name',
      key: 'project_name',
      width: 150,
    },
    {
      title: '订购单价',
      dataIndex: 'order_price',
      key: 'order_price',
      width: 100,
      render: (price?: number) => price ? `¥${price}` : '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={PurchaseStatusColor[status]}>
          {PurchaseStatusLabel[status]}
        </Tag>
      ),
    },
    {
      title: '申请人',
      dataIndex: ['applicant', 'username'],
      key: 'applicant',
      width: 100,
    },
    {
      title: '申请日期',
      dataIndex: 'application_date',
      key: 'application_date',
      width: 120,
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right' as const,
      render: (_: any, record: PurchaseRequest) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
          >
            查看
          </Button>
          {isAdmin && record.status === 'pending' && (
            <>
              <Button
                type="link"
                size="small"
                icon={<CheckOutlined />}
                onClick={() => {
                  Modal.confirm({
                    title: '批准采购申请',
                    content: (
                      <Input.TextArea
                        placeholder="请输入审批意见（可选）"
                        rows={3}
                        onChange={(e) => {
                          (e.target as any).commentValue = e.target.value;
                        }}
                      />
                    ),
                    onOk: () => {
                      const comment = (document.querySelector('textarea') as any)?.value;
                      handleApprove(record.id, 'approve', comment);
                    },
                  });
                }}
              >
                批准
              </Button>
              <Button
                type="link"
                size="small"
                danger
                icon={<CloseOutlined />}
                onClick={() => {
                  Modal.confirm({
                    title: '拒绝采购申请',
                    content: (
                      <Input.TextArea
                        placeholder="请输入拒绝原因（可选）"
                        rows={3}
                      />
                    ),
                    onOk: () => {
                      const comment = (document.querySelector('textarea') as any)?.value;
                      handleApprove(record.id, 'reject', comment);
                    },
                  });
                }}
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
          scroll={{ x: 1800 }}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </div>

      {/* 提交采购申请模态框 */}
      <Modal
        title="提交采购申请"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={800}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Card title="基本信息" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="product_name"
                  label="产品名称"
                  rules={[{ required: true, message: '请输入产品名称' }]}
                >
                  <Input placeholder="请输入产品名称" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="brand" label="品牌">
                  <Input placeholder="请输入品牌" />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={8}>
                <Form.Item
                  name="product_code"
                  label="货号"
                  rules={[{ required: true, message: '请输入货号' }]}
                >
                  <Input placeholder="请输入货号" />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item name="cas_number" label="CAS号">
                  <Input placeholder="请输入CAS号" />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item name="form" label="形态">
                  <Select placeholder="请选择形态">
                    <Option value="solid">固体</Option>
                    <Option value="liquid">液体</Option>
                    <Option value="gas">气体</Option>
                    <Option value="equipment">设备</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="specifications" label="规格">
                  <Input placeholder="请输入规格" />
                </Form.Item>
              </Col>
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
            </Row>
            <Form.Item
              name="purpose"
              label="用途"
              rules={[{ required: true, message: '请输入用途' }]}
            >
              <TextArea rows={2} placeholder="请输入用途" />
            </Form.Item>
          </Card>

          <Card title="申请人信息" size="small" style={{ marginBottom: 16 }}>
            <Form.Item
              name="project_name"
              label="申请项目"
              rules={[{ required: true, message: '请输入申请项目' }]}
            >
              <Input placeholder="请输入申请项目" />
            </Form.Item>
            <Form.Item
              name="delivery_info"
              label="申请人收货信息（具体地址+姓名+电话）"
              rules={[{ required: true, message: '请输入收货信息' }]}
            >
              <TextArea rows={2} placeholder="请输入收货信息" />
            </Form.Item>
          </Card>

          <Card title="采购信息" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={8}>
                <Form.Item name="query_price" label="查询单价（元）">
                  <InputNumber
                    style={{ width: '100%' }}
                    placeholder="请输入查询单价"
                    min={0}
                    precision={2}
                    prefix="¥"
                  />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item name="order_price" label="订购单价（元）">
                  <InputNumber
                    style={{ width: '100%' }}
                    placeholder="请输入订购单价"
                    min={0}
                    precision={2}
                    prefix="¥"
                  />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item name="order_quantity" label="订购数量">
                  <InputNumber
                    style={{ width: '100%' }}
                    placeholder="请输入订购数量"
                    min={0}
                  />
                </Form.Item>
              </Col>
            </Row>
          </Card>

          <Card title="存放信息" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={8}>
                <Form.Item name="campus" label="存放校区">
                  <Input placeholder="请输入存放校区" />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item name="building" label="存放楼宇">
                  <Input placeholder="请输入存放楼宇" />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item name="room" label="存放房间">
                  <Input placeholder="请输入存放房间" />
                </Form.Item>
              </Col>
            </Row>
          </Card>

          <Card title="采购渠道" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={8}>
                <Form.Item name="is_hazardous_platform" valuePropName="checked">
                  <Checkbox>危化品平台采购</Checkbox>
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item name="is_institute_center" valuePropName="checked">
                  <Checkbox>生科院试剂中心采购</Checkbox>
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item name="is_school_warehouse" valuePropName="checked">
                  <Checkbox>学校仓库采购</Checkbox>
                </Form.Item>
              </Col>
            </Row>
          </Card>

          <Card title="其他" size="small">
            <Form.Item name="remarks" label="备注">
              <TextArea rows={2} placeholder="请输入备注" />
            </Form.Item>
          </Card>

          <Form.Item style={{ marginTop: 16 }}>
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

      {/* 查看采购申请详情模态框 */}
      <Modal
        title="采购申请详情"
        open={viewModalVisible}
        onCancel={() => setViewModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setViewModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={900}
      >
        {viewingRequest && (
          <Card>
            <Row gutter={[16, 16]}>
              <Col span={8}>
                <strong>序号：</strong>{viewingRequest.sequence_number}
              </Col>
              <Col span={8}>
                <strong>产品名称：</strong>{viewingRequest.product_name}
              </Col>
              <Col span={8}>
                <strong>品牌：</strong>{viewingRequest.brand || '-'}
              </Col>
              <Col span={8}>
                <strong>货号：</strong>{viewingRequest.product_code}
              </Col>
              <Col span={8}>
                <strong>CAS号：</strong>{viewingRequest.cas_number || '-'}
              </Col>
              <Col span={8}>
                <strong>形态：</strong>{viewingRequest.form || '-'}
              </Col>
              <Col span={8}>
                <strong>规格：</strong>{viewingRequest.specifications || '-'}
              </Col>
              <Col span={8}>
                <strong>数量：</strong>{viewingRequest.quantity}
              </Col>
              <Col span={8}>
                <strong>用途：</strong>{viewingRequest.purpose}
              </Col>
              <Col span={8}>
                <strong>申请项目：</strong>{viewingRequest.project_name}
              </Col>
              <Col span={8}>
                <strong>申请日期：</strong>{viewingRequest.application_date}
              </Col>
              <Col span={24}>
                <strong>收货信息：</strong>{viewingRequest.delivery_info}
              </Col>
              <Col span={8}>
                <strong>查询单价：</strong>{viewingRequest.query_price ? `¥${viewingRequest.query_price}` : '-'}
              </Col>
              <Col span={8}>
                <strong>订购单价：</strong>{viewingRequest.order_price ? `¥${viewingRequest.order_price}` : '-'}
              </Col>
              <Col span={8}>
                <strong>订购数量：</strong>{viewingRequest.order_quantity || '-'}
              </Col>
              <Col span={8}>
                <strong>到货日期：</strong>{viewingRequest.delivery_date || '-'}
              </Col>
              <Col span={8}>
                <strong>到货数量：</strong>{viewingRequest.delivery_quantity || '-'}
              </Col>
              <Col span={8}>
                <strong>存放位置：</strong>
                {[viewingRequest.campus, viewingRequest.building, viewingRequest.room].filter(Boolean).join('/') || '-'}
              </Col>
              <Col span={8}>
                <strong>危化品平台采购：</strong>{viewingRequest.is_hazardous_platform ? '是' : '否'}
              </Col>
              <Col span={8}>
                <strong>生科院试剂中心采购：</strong>{viewingRequest.is_institute_center ? '是' : '否'}
              </Col>
              <Col span={8}>
                <strong>学校仓库采购：</strong>{viewingRequest.is_school_warehouse ? '是' : '否'}
              </Col>
              <Col span={12}>
                <strong>申请人：</strong>{viewingRequest.applicant?.username}
              </Col>
              <Col span={12}>
                <strong>状态：</strong>
                <Tag color={PurchaseStatusColor[viewingRequest.status]}>
                  {PurchaseStatusLabel[viewingRequest.status]}
                </Tag>
              </Col>
              {viewingRequest.approver && (
                <Col span={12}>
                  <strong>审批人：</strong>{viewingRequest.approver.username}
                </Col>
              )}
              {viewingRequest.approval_comment && (
                <Col span={12}>
                  <strong>审批意见：</strong>{viewingRequest.approval_comment}
                </Col>
              )}
              <Col span={24}>
                <strong>备注：</strong>{viewingRequest.remarks || '-'}
              </Col>
            </Row>
          </Card>
        )}
      </Modal>
    </div>
  );
};

export default Purchases;

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
import { getPicks, createPick, approvePick, rejectPick } from '../api/picks';
import { getConsumables } from '../api/consumables';
import { useAuth } from '../contexts/AuthContext';
import type { PickRecord, Consumable, PickFormData, QueryParams } from '../types';
import '../styles/common.scss';

const { Option } = Select;
const { TextArea } = Input;

// 领料管理页面组件
const Picks: React.FC = () => {
  const [records, setRecords] = useState<PickRecord[]>([]);
  const [consumables, setConsumables] = useState<Consumable[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [viewModalVisible, setViewModalVisible] = useState(false);
  const [viewingRecord, setViewingRecord] = useState<PickRecord | null>(null);
  const [activeTab, setActiveTab] = useState('my');
  const [selectedConsumable, setSelectedConsumable] = useState<Consumable | null>(null);
  const [form] = Form.useForm<PickFormData>();
  const { isAdmin } = useAuth();

  // 初始化加载数据
  useEffect(() => {
    fetchRecords();
    fetchConsumables();
  }, [activeTab]);

  // 获取领料记录列表
  const fetchRecords = async () => {
    setLoading(true);
    try {
      // "我的申请" tab: 显示当前用户的所有申请
      // "领料审批" tab: 仅显示待审批的申请
      const params: QueryParams = activeTab === 'my' ? { my: true } : { status: 'pending' };
      const response = await getPicks(params);
      setRecords(response.data.items || []);
    } catch (error) {
      message.error('获取领料记录失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取耗材列表
  const fetchConsumables = async () => {
    try {
      const response = await getConsumables();
      setConsumables(response.data.items || []);
    } catch (error) {
      console.error('获取耗材列表失败:', error);
    }
  };

  // 打开领料申请弹窗
  const handleAdd = () => {
    form.resetFields();
    setSelectedConsumable(null);
    setModalVisible(true);
  };

  // 查看领料记录详情
  const handleView = (record: PickRecord) => {
    setViewingRecord(record);
    setViewModalVisible(true);
  };

  // 处理耗材选择变化
  const handleConsumableChange = (value: number) => {
    const consumable = consumables.find(c => c.id === value);
    setSelectedConsumable(consumable || null);
  };

  // 提交领料申请
  const handleSubmit = async (values: PickFormData) => {
    try {
      await createPick(values);
      message.success('领料申请已提交');
      setModalVisible(false);
      fetchRecords();
    } catch (error: any) {
      const errorMsg = error?.message || '提交失败';
      message.error(errorMsg);
    }
  };

  // 审批领料申请
  const handleApprove = async (id: number, action: 'approve' | 'reject') => {
    try {
      if (action === 'approve') {
        await approvePick(id);
      } else {
        await rejectPick(id, '');
      }
      message.success(action === 'approve' ? '已批准' : '已拒绝');
      fetchRecords();
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
  const columns: ColumnsType<PickRecord> = [
    {
      title: '物品名称',
      dataIndex: ['item', 'name'],
      key: 'item',
    },
    {
      title: '物品编号',
      dataIndex: ['item', 'code'],
      key: 'item_code',
    },
    {
      title: '领用数量',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (quantity: number, record: PickRecord) => `${quantity} ${record.item?.unit}`,
    },
    {
      title: '用途',
      dataIndex: 'purpose',
      key: 'purpose',
      render: (purpose?: string) => purpose || '-',
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
      dataIndex: ['picker', 'username'],
      key: 'picker',
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
      render: (_: any, record: PickRecord) => (
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
      label: '我的领料记录',
    },
    ...(isAdmin ? [{
      key: 'approve',
      label: '领料审批',
    }] : []),
  ];

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">领料管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          提交领料申请
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
          dataSource={records}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </div>

      <Modal
        title="提交领料申请"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="item_id"
            label="选择耗材"
            rules={[{ required: true, message: '请选择耗材' }]}
          >
            <Select
              placeholder="请选择耗材"
              onChange={handleConsumableChange}
            >
              {consumables.filter(c => c.stock > 0).map(consumable => (
                <Option key={consumable.id} value={consumable.id}>
                  {consumable.code} - {consumable.name} (库存: {consumable.stock} {consumable.unit})
                </Option>
              ))}
            </Select>
          </Form.Item>
          {selectedConsumable && (
            <div style={{ marginBottom: 16, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
              <p><strong>当前库存：</strong>{selectedConsumable.stock} {selectedConsumable.unit}</p>
              <p><strong>最低库存：</strong>{selectedConsumable.min_stock} {selectedConsumable.unit}</p>
            </div>
          )}
          <Form.Item
            name="quantity"
            label="领用数量"
            rules={[
              { required: true, message: '请输入领用数量' },
              {
                validator: (_, value) => {
                  if (selectedConsumable && value > selectedConsumable.stock) {
                    return Promise.reject(new Error('领用数量不能超过当前库存'));
                  }
                  return Promise.resolve();
                },
              },
            ]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="请输入领用数量"
              min={1}
              max={selectedConsumable?.stock}
            />
          </Form.Item>
          <Form.Item name="purpose" label="用途">
            <TextArea rows={4} placeholder="请输入用途（可选）" />
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
        title="领料记录详情"
        open={viewModalVisible}
        onCancel={() => setViewModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setViewModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={600}
      >
        {viewingRecord && (
          <Card>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <strong>物品名称：</strong>{viewingRecord.item?.name}
              </Col>
              <Col span={12}>
                <strong>物品编号：</strong>{viewingRecord.item?.code}
              </Col>
              <Col span={12}>
                <strong>领用数量：</strong>{viewingRecord.quantity} {viewingRecord.item?.unit}
              </Col>
              <Col span={12}>
                <strong>状态：</strong>
                <Tag color={getStatusColor(viewingRecord.status)}>
                  {getStatusText(viewingRecord.status)}
                </Tag>
              </Col>
              <Col span={12}>
                <strong>申请人：</strong>{viewingRecord.picker?.username}
              </Col>
              <Col span={12}>
                <strong>申请时间：</strong>{new Date(viewingRecord.created_at).toLocaleString('zh-CN')}
              </Col>
              {viewingRecord.approver && (
                <Col span={12}>
                  <strong>审批人：</strong>{viewingRecord.approver.username}
                </Col>
              )}
              {viewingRecord.approved_at && (
                <Col span={12}>
                  <strong>审批时间：</strong>{new Date(viewingRecord.approved_at).toLocaleString('zh-CN')}
                </Col>
              )}
              <Col span={24}>
                <strong>用途：</strong>{viewingRecord.purpose || '-'}
              </Col>
            </Row>
          </Card>
        )}
      </Modal>
    </div>
  );
};

export default Picks;

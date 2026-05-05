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
  Col
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  SwapOutlined,
  RollbackOutlined,
  EyeOutlined
} from '@ant-design/icons';
import { getBorrows, createBorrow, returnAsset } from '../api/borrows';
import { getAssets } from '../api/assets';
import { useAuth } from '../contexts/AuthContext';
import type { BorrowRecord, AssetLite, BorrowFormData, QueryParams } from '../types';
import '../styles/common.scss';

const { Option } = Select;
const { TextArea } = Input;

// 资产借用页面组件
const Borrows: React.FC = () => {
  const [records, setRecords] = useState<BorrowRecord[]>([]);
  const [availableAssets, setAvailableAssets] = useState<AssetLite[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [viewModalVisible, setViewModalVisible] = useState(false);
  const [viewingRecord, setViewingRecord] = useState<BorrowRecord | null>(null);
  const [form] = Form.useForm<BorrowFormData>();
  const { user, isAdmin } = useAuth();

  // 初始化加载数据
  useEffect(() => {
    fetchRecords();
    fetchAvailableAssets();
  }, []);

  // 获取借用记录列表
  const fetchRecords = async () => {
    setLoading(true);
    try {
      // 非管理员只能查看自己的借用记录，管理员可以查看所有记录
      const params: QueryParams = isAdmin ? {} : { my: true };
      const response = await getBorrows(params);
      setRecords(response.data.items || []);
    } catch (error) {
      message.error('获取借用记录失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取可用资产列表
  const fetchAvailableAssets = async () => {
    try {
      const params: QueryParams = { status: 'available' };
      const response = await getAssets(params);
      setAvailableAssets(response.data.items || []);
    } catch (error) {
      console.error('获取可用资产失败:', error);
    }
  };

  // 打开借用弹窗
  const handleBorrow = () => {
    form.resetFields();
    setModalVisible(true);
  };

  // 查看借用记录详情
  const handleView = (record: BorrowRecord) => {
    setViewingRecord(record);
    setViewModalVisible(true);
  };

  // 提交借用申请
  const handleSubmit = async (values: BorrowFormData) => {
    try {
      await createBorrow(values);
      message.success('借用成功');
      setModalVisible(false);
      fetchRecords();
      fetchAvailableAssets();
    } catch (error: any) {
      const errorMsg = error?.message || '借用失败';
      message.error(errorMsg);
    }
  };

  // 归还资产
  const handleReturn = async (recordId: number) => {
    try {
      await returnAsset(recordId);
      message.success('归还成功');
      fetchRecords();
      fetchAvailableAssets();
    } catch (error: any) {
      const errorMsg = error?.message || '归还失败';
      message.error(errorMsg);
    }
  };

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      borrowed: 'blue',
      returned: 'green',
    };
    return colors[status] || 'default';
  };

  // 获取状态文本
  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      borrowed: '借用中',
      returned: '已归还',
    };
    return texts[status] || status;
  };

  // 表格列定义
  const columns: ColumnsType<BorrowRecord> = [
    {
      title: '资产名称',
      dataIndex: ['asset', 'name'],
      key: 'asset',
    },
    {
      title: '资产编号',
      dataIndex: ['asset', 'code'],
      key: 'asset_code',
    },
    {
      title: '借用人',
      dataIndex: ['borrower', 'username'],
      key: 'borrower',
    },
    {
      title: '借用日期',
      dataIndex: 'borrow_date',
      key: 'borrow_date',
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '归还日期',
      dataIndex: 'return_date',
      key: 'return_date',
      render: (date?: string) => date ? new Date(date).toLocaleString('zh-CN') : '-',
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
      title: '操作',
      key: 'action',
      render: (_: any, record: BorrowRecord) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
          >
            查看
          </Button>
          {record.status === 'borrowed' && record.borrower.id === user?.id && (
            <Button
              type="link"
              icon={<RollbackOutlined />}
              onClick={() => handleReturn(record.id)}
            >
              归还
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">资产借用</h2>
        <Button type="primary" icon={<SwapOutlined />} onClick={handleBorrow}>
          借用资产
        </Button>
      </div>

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
        title="借用资产"
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
            <Select placeholder="请选择可用的资产">
              {availableAssets.map(asset => (
                <Option key={asset.id} value={asset.id}>
                  {asset.lab_asset_code} - {asset.name}
                </Option>
              ))}
            </Select>
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
        title="借用记录详情"
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
                <strong>资产名称：</strong>{viewingRecord.asset?.name}
              </Col>
              <Col span={12}>
                <strong>资产编号：</strong>{viewingRecord.asset?.lab_asset_code}
              </Col>
              <Col span={12}>
                <strong>借用日期：</strong>{new Date(viewingRecord.borrow_date).toLocaleString('zh-CN')}
              </Col>
              <Col span={12}>
                <strong>归还日期：</strong>
                {viewingRecord.return_date ? new Date(viewingRecord.return_date).toLocaleString('zh-CN') : '-'}
              </Col>
              <Col span={12}>
                <strong>状态：</strong>
                <Tag color={getStatusColor(viewingRecord.status)}>
                  {getStatusText(viewingRecord.status)}
                </Tag>
              </Col>
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

export default Borrows;

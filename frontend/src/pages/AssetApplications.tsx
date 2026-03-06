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
  Tabs,
  Descriptions
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import type { TabsProps } from 'antd';
import {
  PlusOutlined,
  CheckOutlined,
  CloseOutlined,
  EyeOutlined
} from '@ant-design/icons';
import {
  getAssetApplications,
  createAssetApplication,
  approveAssetApplication
} from '../api/assetApplications';
import { getAssets } from '../api/assets';
import { useAuth } from '../contexts/AuthContext';
import {
  ApplicationTypeLabels,
  ApplicationStatusLabel
} from '../api/assetApplications';
import type {
  AssetApplication,
  AssetLite,
  AssetApplicationFormData,
  QueryParams
} from '../types';
import '../styles/common.scss';

const { Option } = Select;
const { TextArea } = Input;

// 资产业务申请页面组件
const AssetApplications: React.FC = () => {
  const [applications, setApplications] = useState<AssetApplication[]>([]);
  const [assets, setAssets] = useState<AssetLite[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [viewModalVisible, setViewModalVisible] = useState(false);
  const [viewingApplication, setViewingApplication] = useState<AssetApplication | null>(null);
  const [activeTab, setActiveTab] = useState('my');
  const [applicationType, setApplicationType] = useState<string>('custodian_change');
  const [selectedAsset, setSelectedAsset] = useState<AssetLite | null>(null);
  const [form] = Form.useForm<AssetApplicationFormData>();
  const { isAdmin } = useAuth();

  // 初始化加载数据
  useEffect(() => {
    fetchApplications();
    fetchAssets();
  }, [activeTab]);

  // 获取业务申请列表
  const fetchApplications = async () => {
    setLoading(true);
    try {
      const params: QueryParams = activeTab === 'my'
        ? { my: true }
        : { status: 'pending' };
      const response = await getAssetApplications(params);
      setApplications(response.data.items || []);
    } catch (error) {
      message.error('获取业务申请列表失败');
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

  // 打开申请弹窗
  const handleAdd = () => {
    form.resetFields();
    setSelectedAsset(null);
    setApplicationType('custodian_change');
    setModalVisible(true);
  };

  // 查看申请详情
  const handleView = (record: AssetApplication) => {
    setViewingApplication(record);
    setViewModalVisible(true);
  };

  // 处理资产选择变化
  const handleAssetChange = (value: number) => {
    const asset = assets.find(a => a.id === value);
    setSelectedAsset(asset || null);
  };

  // 提交申请
  const handleSubmit = async (values: any) => {
    try {
      const content: any = {};

      // 根据申请类型构建不同的内容
      switch (applicationType) {
        case 'custodian_change':
          content.new_custodian_id = values.new_custodian_id;
          content.reason = values.reason;
          break;
        case 'allocation':
          content.to_campus = values.to_campus;
          content.to_building = values.to_building;
          content.to_room = values.to_room;
          content.reason = values.reason;
          break;
        case 'repair':
          content.fault_description = values.fault_description;
          content.urgent = values.urgent || false;
          break;
        case 'return':
        case 'scrap':
        case 'loss':
          content.reason = values.reason;
          content.description = values.description;
          break;
      }

      const formData: AssetApplicationFormData = {
        asset_id: values.asset_id,
        application_type: applicationType,
        content: content
      };

      await createAssetApplication(formData);
      message.success('申请已提交');
      setModalVisible(false);
      fetchApplications();
    } catch (error: any) {
      const errorMsg = error?.message || '提交失败';
      message.error(errorMsg);
    }
  };

  // 审批申请
  const handleApprove = async (id: number, action: 'approve' | 'reject') => {
    try {
      await approveAssetApplication(id, action);
      message.success(action === 'approve' ? '已批准' : '已拒绝');
      fetchApplications();
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
      processing: 'blue',
      completed: 'default',
    };
    return colors[status] || 'default';
  };

  // 获取申请类型颜色
  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      custodian_change: 'blue',
      allocation: 'cyan',
      repair: 'orange',
      return: 'green',
      scrap: 'red',
      loss: 'purple',
    };
    return colors[type] || 'default';
  };

  // 表格列定义
  const columns: ColumnsType<AssetApplication> = [
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
      title: '申请类型',
      dataIndex: 'application_type',
      key: 'application_type',
      render: (type: string) => (
        <Tag color={getTypeColor(type)}>{ApplicationTypeLabels[type] || type}</Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>{ApplicationStatusLabel[status] || status}</Tag>
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
      render: (_: any, record: AssetApplication) => (
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
      label: '我的业务申请',
    },
    ...(isAdmin ? [{
      key: 'approve',
      label: '业务审批',
    }] : []),
  ];

  // 渲染动态表单内容
  const renderFormFields = () => {
    const commonFields = (
      <>
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
                {asset.lab_asset_code} - {asset.name}
              </Option>
            ))}
          </Select>
        </Form.Item>
      </>
    );

    switch (applicationType) {
      case 'custodian_change':
        return (
          <>
            {commonFields}
            <Form.Item
              name="new_custodian_id"
              label="新保管人"
              rules={[{ required: true, message: '请选择新保管人' }]}
            >
              <Select placeholder="请选择新保管人">
                {/* TODO: 从用户列表获取 */}
                <Option value={1}>管理员</Option>
                <Option value={2}>测试用户</Option>
              </Select>
            </Form.Item>
            <Form.Item
              name="reason"
              label="变更原因"
              rules={[{ required: true, message: '请输入变更原因' }]}
            >
              <TextArea rows={4} placeholder="请输入变更原因" />
            </Form.Item>
          </>
        );

      case 'allocation':
        return (
          <>
            {commonFields}
            {selectedAsset && (
              <Card size="small" style={{ marginBottom: 16 }}>
                <p><strong>当前位置：</strong>{selectedAsset.location}</p>
              </Card>
            )}
            <Row gutter={16}>
              <Col span={8}>
                <Form.Item
                  name="to_campus"
                  label="新校区"
                  rules={[{ required: true, message: '请输入校区' }]}
                >
                  <Input placeholder="如：本部" />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  name="to_building"
                  label="新楼宇"
                  rules={[{ required: true, message: '请输入楼宇' }]}
                >
                  <Input placeholder="如：实验楼A" />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  name="to_room"
                  label="新房间"
                >
                  <Input placeholder="如：301" />
                </Form.Item>
              </Col>
            </Row>
            <Form.Item
              name="reason"
              label="调拨原因"
              rules={[{ required: true, message: '请输入调拨原因' }]}
            >
              <TextArea rows={4} placeholder="请输入调拨原因" />
            </Form.Item>
          </>
        );

      case 'repair':
        return (
          <>
            {commonFields}
            <Form.Item
              name="fault_description"
              label="故障描述"
              rules={[{ required: true, message: '请描述故障情况' }]}
            >
              <TextArea rows={4} placeholder="请详细描述设备故障情况" />
            </Form.Item>
            <Form.Item
              name="urgent"
              label="是否紧急"
              valuePropName="checked"
            >
              <Select defaultValue={false}>
                <Option value={false}>普通</Option>
                <Option value={true}>紧急</Option>
              </Select>
            </Form.Item>
          </>
        );

      case 'return':
      case 'scrap':
      case 'loss':
        return (
          <>
            {commonFields}
            <Form.Item
              name="reason"
              label={`${ApplicationTypeLabels[applicationType]}原因`}
              rules={[{ required: true, message: '请输入原因' }]}
            >
              <TextArea rows={4} placeholder={`请输入${ApplicationTypeLabels[applicationType]}原因`} />
            </Form.Item>
            <Form.Item
              name="description"
              label="详细说明"
            >
              <TextArea rows={3} placeholder="请提供更多详细信息（可选）" />
            </Form.Item>
          </>
        );

      default:
        return null;
    }
  };

  // 解析申请内容
  const parseContent = (content: any) => {
    try {
      if (typeof content === 'string') {
        return JSON.parse(content);
      }
      return content;
    } catch {
      return {};
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">资产业务</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          申请办理业务
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
          dataSource={applications}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </div>

      <Modal
        title="申请办理业务"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={700}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            label="业务类型"
            initialValue="custodian_change"
          >
            <Select
              value={applicationType}
              onChange={setApplicationType}
            >
              <Option value="custodian_change">保管人变更</Option>
              <Option value="allocation">资产调拨</Option>
              <Option value="repair">设备维修</Option>
              <Option value="return">退库</Option>
              <Option value="scrap">报废</Option>
              <Option value="loss">报失报损</Option>
            </Select>
          </Form.Item>

          {renderFormFields()}

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                提交申请
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="业务申请详情"
        open={viewModalVisible}
        onCancel={() => setViewModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setViewModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={700}
      >
        {viewingApplication && (
          <Card>
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="资产名称">
                {viewingApplication.asset?.name}
              </Descriptions.Item>
              <Descriptions.Item label="资产编号">
                {viewingApplication.asset?.lab_asset_code}
              </Descriptions.Item>
              <Descriptions.Item label="申请类型">
                <Tag color={getTypeColor(viewingApplication.application_type)}>
                  {ApplicationTypeLabels[viewingApplication.application_type]}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                <Tag color={getStatusColor(viewingApplication.status)}>
                  {ApplicationStatusLabel[viewingApplication.status]}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="申请人">
                {viewingApplication.applicant?.username}
              </Descriptions.Item>
              <Descriptions.Item label="申请时间">
                {new Date(viewingApplication.created_at).toLocaleString('zh-CN')}
              </Descriptions.Item>
              {viewingApplication.approver && (
                <Descriptions.Item label="审批人">
                  {viewingApplication.approver.username}
                </Descriptions.Item>
              )}
              {viewingApplication.approval_comment && (
                <Descriptions.Item label="审批意见" span={2}>
                  {viewingApplication.approval_comment}
                </Descriptions.Item>
              )}
            </Descriptions>

            <Card title="申请内容" size="small" style={{ marginTop: 16 }}>
              <pre style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
                {JSON.stringify(parseContent(viewingApplication.content), null, 2)}
              </pre>
            </Card>
          </Card>
        )}
      </Modal>
    </div>
  );
};

export default AssetApplications;

import React, { useEffect, useState, useRef, useMemo, useCallback, memo } from 'react';
import dayjs, { Dayjs } from 'dayjs';
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  InputNumber,
  message,
  Popconfirm,
  Tag,
  Card,
  Row,
  Col,
  Tabs,
  Image,
  Upload,
  Spin
} from 'antd';
import type { FormInstance } from 'antd/es/form';
import type { ColumnsType } from 'antd/es/table';
import type { UploadProps } from 'antd/es/upload';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  PlusSquareOutlined,
} from '@ant-design/icons';
import { getAssets, getAsset, createAsset, updateAsset, deleteAsset, AssetTypeLabels, AssetStatusLabel, AssetStatusColor } from '../api/assets';
import { getUsersSimple } from '../api/users';
import { useAuth } from '../contexts/AuthContext';
import type { Asset, AssetLite, QueryParams } from '../types';
import type { UserSimple } from '../api/users';
import { getImageUrl } from '../utils/image';
import '../styles/common.scss';



const { Option } = Select;
const { TextArea } = Input;

interface AssetFormValues {
  lab_asset_code: string;
  school_asset_code?: string;
  name: string;
  asset_type: 'equipment' | 'software';
  model: string;
  specifications?: string;
  manufacturer?: string;
  purchase_price?: number;
  department: string;
  current_status?: string;
  campus: string;
  building: string;
  room?: string;
  purchase_date?: Dayjs | null;
  custodian_id?: number;
  custodian_phone?: string;
  // 图片文件（用于上传）
  photo_full?: File;
  photo_model?: File;
  photo_tag?: File;
  // 图片URL（编辑时保留原有URL）
  photo_full_url?: string;
  photo_model_url?: string;
  photo_tag_url?: string;
  remarks?: string;
}

interface ImageUploadProps {
  value?: File;
  imageUrl?: string;
  onChange?: (file?: File) => void;
  label: string;
}

// 图片上传组件（本地预览，不上传到服务器）
// 使用 memo 优化性能，避免不必要的重新渲染
const ImageUpload: React.FC<ImageUploadProps> = memo(({ value, imageUrl, onChange, label }) => {
  const [previewUrl, setPreviewUrl] = useState<string>('');

  // 初始化预览
  useEffect(() => {
    if (value instanceof File) {
      setPreviewUrl(URL.createObjectURL(value));
    } else if (imageUrl) {
      setPreviewUrl(getImageUrl(imageUrl));
    } else {
      setPreviewUrl('');
    }
    return () => {
      if (value instanceof File && previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [value, imageUrl]);

  const handleSelect: UploadProps['beforeUpload'] = useCallback((selectedFile: any) => {
    // 验证文件类型
    const isImage = selectedFile.type.startsWith('image/');
    if (!isImage) {
      message.error('只能上传图片文件');
      return Upload.LIST_IGNORE;
    }
    // 验证文件大小（5MB）
    const isLt5M = selectedFile.size / 1024 / 1024 < 5;
    if (!isLt5M) {
      message.error('图片大小不能超过 5MB');
      return Upload.LIST_IGNORE;
    }

    onChange?.(selectedFile);
    return Upload.LIST_IGNORE;
  }, [onChange]);

  const handleRemove = useCallback(() => {
    onChange?.(undefined);
  }, [onChange]);

  const uploadButton = (
    <div>
      <PlusSquareOutlined />
      <div style={{ marginTop: 8 }}>上传</div>
    </div>
  );

  return (
    <div>
      <Upload
        listType="picture-card"
        fileList={previewUrl ? [{
          uid: '-1',
          name: value?.name || 'image.png',
          status: 'done',
          url: previewUrl,
        }] : []}
        beforeUpload={handleSelect}
        onRemove={handleRemove}
        maxCount={1}
        accept="image/*"
      >
        {previewUrl ? undefined : uploadButton}
      </Upload>
      <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>{label}</div>
    </div>
  );
});

ImageUpload.displayName = 'ImageUpload';

const Assets: React.FC = () => {
  const [assets, setAssets] = useState<AssetLite[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [viewModalVisible, setViewModalVisible] = useState(false);
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null);
  const [viewingAsset, setViewingAsset] = useState<Asset | null>(null);
  const [activeTab, setActiveTab] = useState<'equipment' | 'software' | 'all'>('all');
  const [filters, setFilters] = useState<QueryParams>({});
  const [submitting, setSubmitting] = useState(false);
  const [users, setUsers] = useState<UserSimple[]>([]);
  const [usersLoading, setUsersLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [form] = Form.useForm<AssetFormValues>();
  const { isAdmin, user: currentUser } = useAuth();

  // 防止并发请求的 ref
  const isFetchingRef = useRef(false);
  // 跟踪用户列表是否已加载
  const usersLoadedRef = useRef(false);

  useEffect(() => {
    fetchAssets();
  }, []);

  // 获取用户列表 - 使用 useCallback 优化
  const fetchUsers = useCallback(async () => {
    // 如果已经加载过，直接返回
    if (usersLoadedRef.current) return;
    
    usersLoadedRef.current = true;
    setUsersLoading(true);
    try {
      const response = await getUsersSimple({ is_active: true });
      setUsers(response.data || []);
    } catch (error) {
      message.error('获取用户列表失败');
    } finally {
      setUsersLoading(false);
    }
  }, []);

  // 使用 useMemo 稳定化 params 引用，避免不必要的重新请求
  const memoizedParams = useMemo(() => {
    const cleanParams: QueryParams = { ...filters };
    if (activeTab !== 'all') {
      cleanParams.asset_type = activeTab;
    }
    (Object.keys(cleanParams) as Array<keyof QueryParams>).forEach(key => {
      if (cleanParams[key] === undefined || cleanParams[key] === '' || cleanParams[key] === false) {
        delete cleanParams[key];
      }
    });
    return cleanParams;
  }, [activeTab, filters]);

  useEffect(() => {
    fetchAssets();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [memoizedParams]);

  const fetchAssets = async () => {
    // 防止并发请求
    if (isFetchingRef.current) {
      return;
    }
    isFetchingRef.current = true;

    setLoading(true);
    try {
      const response = await getAssets(memoizedParams);
      setAssets(response.data.items || []);
    } catch (error) {
      message.error('获取资产列表失败');
    } finally {
      setLoading(false);
      isFetchingRef.current = false;
    }
  };

  const handleAdd = useCallback(async () => {
    // 先显示加载遮罩
    setDetailLoading(true);
    setEditingAsset(null);
    form.resetFields();
    
    // 加载用户列表（首次才真正请求）+ 最小延迟确保视觉反馈
    await Promise.all([
      fetchUsers(),
      new Promise(resolve => setTimeout(resolve, 200))
    ]);
    
    // 加载完成后打开模态框
    setModalVisible(true);
    setDetailLoading(false);
  }, [form, fetchUsers]);

  const handleEdit = useCallback(async (record: AssetLite) => {
    // 先显示加载遮罩
    setDetailLoading(true);
    fetchUsers();
    
    try {
      const response = await getAsset(record.id);
      const fullAsset = response.data;
      setEditingAsset(fullAsset);
      form.setFieldsValue({
        ...fullAsset,
        custodian_id: fullAsset.manager?.id,
        purchase_date: fullAsset.purchase_date ? dayjs(fullAsset.purchase_date) : null,
      });
      // 数据加载完成后打开模态框
      setModalVisible(true);
    } catch (error) {
      message.error('获取资产详情失败');
    } finally {
      setDetailLoading(false);
    }
  }, [form, fetchUsers]);

  const handleView = useCallback(async (record: AssetLite) => {
    // 先显示加载遮罩
    setDetailLoading(true);
    try {
      const response = await getAsset(record.id);
      setViewingAsset(response.data);
      // 数据加载完成后打开模态框
      setViewModalVisible(true);
    } catch (error) {
      message.error('获取资产详情失败');
    } finally {
      setDetailLoading(false);
    }
  }, []);

  const handleDelete = useCallback(async (id: number) => {
    try {
      await deleteAsset(id);
      message.success('删除成功');
      fetchAssets();
    } catch (error: any) {
      const errorMsg = error?.message || '删除失败';
      message.error(errorMsg);
    }
  }, [fetchAssets]);

  const handleSubmit = async (values: AssetFormValues) => {
    setSubmitting(true);
    try {
      // 构建表单数据
      const formData = new FormData();

      // 添加基本字段
      formData.append('lab_asset_code', values.lab_asset_code);
      if (values.school_asset_code) formData.append('school_asset_code', values.school_asset_code);
      formData.append('name', values.name);
      formData.append('asset_type', values.asset_type);
      formData.append('model', values.model);
      if (values.specifications) formData.append('specifications', values.specifications);
      if (values.manufacturer) formData.append('manufacturer', values.manufacturer);
      if (values.purchase_price) formData.append('purchase_price', values.purchase_price.toString());
      formData.append('department', values.department);
      if (values.current_status) formData.append('current_status', values.current_status);
      formData.append('campus', values.campus);
      formData.append('building', values.building);
      if (values.room) formData.append('room', values.room);
      if (values.purchase_date) formData.append('purchase_date', values.purchase_date.format('YYYY-MM-DD'));

      // 处理保管人信息 - 从用户ID获取，同时设置 manager_id
      if (values.custodian_id) {
        const selectedUser = users.find(u => u.id === values.custodian_id);
        if (selectedUser) {
          formData.append('custodian_name', selectedUser.username);
          formData.append('manager_id', selectedUser.id.toString());
        }
      } else if (currentUser) {
        // 如果没有选择保管人，使用当前登录用户
        formData.append('custodian_name', currentUser.username);
        formData.append('manager_id', currentUser.id.toString());
      }
      if (values.custodian_phone) formData.append('custodian_phone', values.custodian_phone);

      if (values.remarks) formData.append('remarks', values.remarks);

      // 添加图片文件（新增或更新了图片）
      if (values.photo_full instanceof File) {
        formData.append('photo_full', values.photo_full);
      } else if (values.photo_full_url) {
        formData.append('photo_full_url', values.photo_full_url);
      }

      if (values.photo_model instanceof File) {
        formData.append('photo_model', values.photo_model);
      } else if (values.photo_model_url) {
        formData.append('photo_model_url', values.photo_model_url);
      }

      if (values.photo_tag instanceof File) {
        formData.append('photo_tag', values.photo_tag);
      } else if (values.photo_tag_url) {
        formData.append('photo_tag_url', values.photo_tag_url);
      }

      if (editingAsset) {
        await updateAsset(editingAsset.id, formData);
        message.success('更新成功');
      } else {
        await createAsset(formData);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchAssets();
    } catch (error: any) {
      const errorMsg = error?.message || (editingAsset ? '更新失败' : '创建失败');
      message.error(errorMsg);
    } finally {
      setSubmitting(false);
    }
  };

  const columns: ColumnsType<AssetLite> = [
    {
      title: '序号',
      key: 'index',
      width: 60,
      render: (_: any, __: AssetLite, index: number) => index + 1,
    },
    {
      title: '编号',
      dataIndex: 'lab_asset_code',
      key: 'lab_asset_code',
      width: 140,
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 150,
    },
    {
      title: '所属院校',
      dataIndex: 'department',
      key: 'department',
      width: 120,
    },
    {
      title: '存放位置',
      dataIndex: 'location',
      key: 'location',
      width: 150,
    },
    {
      title: '现状',
      dataIndex: 'current_status',
      key: 'current_status',
      width: 100,
      render: (status: string) => (
        <Tag color={AssetStatusColor[status] || 'default'}>
          {AssetStatusLabel[status] || status}
        </Tag>
      ),
    },
    {
      title: '保管人',
      dataIndex: 'custodian_name',
      key: 'custodian_name',
      width: 100,
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      fixed: 'right' as const,
      render: (_: any, record: AssetLite) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
          >
            查看
          </Button>
          {isAdmin && (
            <>
              <Button
                type="link"
                size="small"
                icon={<EditOutlined />}
                onClick={() => handleEdit(record)}
              >
                编辑
              </Button>
              <Popconfirm
                title="确定要删除这个资产吗？"
                onConfirm={() => handleDelete(record.id)}
                okText="确定"
                cancelText="取消"
              >
                <Button type="link" size="small" danger icon={<DeleteOutlined />}>
                  删除
                </Button>
              </Popconfirm>
            </>
          )}
        </Space>
      ),
    },
  ];

// 自定义图片上传表单项组件 - 移到组件外部，使用 memo 优化
interface ImageUploadFormItemProps {
  fileName: keyof AssetFormValues;
  urlName: keyof AssetFormValues;
  label: string;
  formInstance: FormInstance<AssetFormValues>;
}

const ImageUploadFormItem = memo<ImageUploadFormItemProps>(({ fileName, urlName, label, formInstance }) => {
  const [file, setFile] = useState<File | undefined>();
  const [imageUrl, setImageUrl] = useState<string>('');

  // 使用 Form.useWatch 来监听字段变化
  const watchedFile = Form.useWatch(fileName as keyof AssetFormValues, formInstance) as File | undefined;
  const watchedUrl = Form.useWatch(urlName as keyof AssetFormValues, formInstance) as string | undefined;

  useEffect(() => {
    setFile(watchedFile);
    setImageUrl(watchedUrl || '');
  }, [watchedFile, watchedUrl]);

  const handleChange = (newFile?: File) => {
    setFile(newFile);
    formInstance.setFieldValue(fileName, newFile);
  };

  return (
    <ImageUpload
      value={file}
      imageUrl={imageUrl}
      onChange={handleChange}
      label={label}
    />
  );
});

ImageUploadFormItem.displayName = 'ImageUploadFormItem';

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">资产管理</h2>
        <Space className="page-actions">
          <Select
            placeholder="按状态筛选"
            style={{ width: 120 }}
            allowClear
            onChange={(value) => {
              const newFilters = { ...filters, status: value };
              setFilters(newFilters);
            }}
          >
            <Option value="in_use">在用</Option>
            <Option value="borrowed">外借</Option>
            <Option value="repair">报修</Option>
            <Option value="returned">退库</Option>
            <Option value="scrapped">报废</Option>
          </Select>
          {isAdmin && (
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              添加资产
            </Button>
          )}
        </Space>
      </div>

      <Tabs
        activeKey={activeTab}
        onChange={(key) => setActiveTab(key as 'equipment' | 'software' | 'all')}
        style={{ marginBottom: 16 }}
      >
        <Tabs.TabPane tab="仪器设备" key="equipment" />
        <Tabs.TabPane tab="软件" key="software" />
        <Tabs.TabPane tab="全部" key="all" />
      </Tabs>

      <div className="table-container">
        <Table
          columns={columns}
          dataSource={assets}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1000 }}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </div>

      {/* 添加/编辑资产模态框 */}
      <Modal
        title={editingAsset ? '编辑资产' : '添加资产'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={900}
        centered={true}
        styles={{ body: { maxHeight: 'calc(100vh - 200px)', overflowY: 'auto' } }}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Card title="基本信息" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="name"
                  label="资产名称"
                  rules={[{ required: true, message: '请输入资产名称' }]}
                >
                  <Input placeholder="请输入资产名称" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="asset_type"
                  label="资产类型"
                  rules={[{ required: true, message: '请选择资产类型' }]}
                  initialValue="equipment"
                >
                  <Select placeholder="请选择资产类型">
                    <Option value="equipment">仪器设备</Option>
                    <Option value="software">软件</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="lab_asset_code"
                  label="课题组资产编号"
                  rules={[{ required: true, message: '请输入课题组资产编号' }]}
                >
                  <Input placeholder="格式：DC+年份+序号" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="school_asset_code" label="学校资产编号">
                  <Input placeholder="请输入学校资产编号" />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="model"
                  label="型号"
                  rules={[{ required: true, message: '请输入型号' }]}
                >
                  <Input placeholder="请输入型号" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="manufacturer" label="生产厂家">
                  <Input placeholder="请输入生产厂家" />
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
                  name="department"
                  label="院系归属"
                  rules={[{ required: true, message: '请输入院系归属' }]}
                >
                  <Input placeholder="请输入院系归属" />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={8}>
                <Form.Item name="purchase_price" label="采购价格">
                  <InputNumber
                    style={{ width: '100%' }}
                    placeholder="请输入采购价格"
                    min={0}
                    precision={2}
                    prefix="¥"
                  />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item name="purchase_date" label="购买日期">
                  <DatePicker style={{ width: '100%' }} />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  name="current_status"
                  label="资产现状"
                  initialValue="in_use"
                >
                  <Select>
                    <Option value="in_use">在用</Option>
                    <Option value="borrowed">外借</Option>
                    <Option value="repair">报修</Option>
                    <Option value="returned">退库</Option>
                    <Option value="scrapped">报废</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>
          </Card>

          <Card title="存放信息" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={8}>
                <Form.Item
                  name="campus"
                  label="存放校区"
                  rules={[{ required: true, message: '请输入存放校区' }]}
                >
                  <Input placeholder="请输入存放校区" />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  name="building"
                  label="存放楼宇"
                  rules={[{ required: true, message: '请输入存放楼宇' }]}
                >
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

          <Card title="保管人信息" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="custodian_id"
                  label="课题组保管人"
                  rules={[{ required: true, message: '请选择保管人' }]}
                >
                  <Select
                    placeholder="请选择保管人"
                    loading={usersLoading}
                    showSearch
                    options={users.map(user => ({ label: user.username, value: user.id }))}
                  />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="custodian_phone" label="保管人联系电话">
                  <Input placeholder="请输入联系电话" />
                </Form.Item>
              </Col>
            </Row>
          </Card>

          <Card title="资产照片" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={8}>
                <div style={{ marginBottom: 8 }}>资产全貌照片</div>
                <ImageUploadFormItem fileName="photo_full" urlName="photo_full_url" label="资产全貌照片" formInstance={form} />
                <Form.Item name="photo_full" hidden><Input /></Form.Item>
                <Form.Item name="photo_full_url" hidden><Input /></Form.Item>
              </Col>
              <Col span={8}>
                <div style={{ marginBottom: 8 }}>型号铭牌近照</div>
                <ImageUploadFormItem fileName="photo_model" urlName="photo_model_url" label="型号铭牌近照" formInstance={form} />
                <Form.Item name="photo_model" hidden><Input /></Form.Item>
                <Form.Item name="photo_model_url" hidden><Input /></Form.Item>
              </Col>
              <Col span={8}>
                <div style={{ marginBottom: 8 }}>固定资产铭牌近照</div>
                <ImageUploadFormItem fileName="photo_tag" urlName="photo_tag_url" label="固定资产铭牌近照" formInstance={form} />
                <Form.Item name="photo_tag" hidden><Input /></Form.Item>
                <Form.Item name="photo_tag_url" hidden><Input /></Form.Item>
              </Col>
            </Row>
          </Card>

          <Card title="其他" size="small">
            <Form.Item name="remarks" label="备注">
              <TextArea rows={3} placeholder="请输入备注" />
            </Form.Item>
          </Card>

          <Form.Item style={{ marginTop: 16 }}>
            <Space>
              <Button type="primary" htmlType="submit" loading={submitting}>
                {editingAsset ? '更新' : '创建'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 查看资产详情模态框 */}
      <Modal
        title="资产详情"
        open={viewModalVisible}
        onCancel={() => setViewModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setViewModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={900}
        centered={true}
        styles={{ body: { maxHeight: 'calc(100vh - 200px)', overflowY: 'auto' } }}
      >
        {viewingAsset && (
          <Card>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <strong>课题组资产编号：</strong>{viewingAsset.lab_asset_code}
              </Col>
              <Col span={12}>
                <strong>学校资产编号：</strong>{viewingAsset.school_asset_code || '-'}
              </Col>
              <Col span={12}>
                <strong>资产名称：</strong>{viewingAsset.name}
              </Col>
              <Col span={12}>
                <strong>资产类型：</strong>{AssetTypeLabels[viewingAsset.asset_type]}
              </Col>
              <Col span={12}>
                <strong>型号：</strong>{viewingAsset.model}
              </Col>
              <Col span={12}>
                <strong>生产厂家：</strong>{viewingAsset.manufacturer || '-'}
              </Col>
              <Col span={12}>
                <strong>规格：</strong>{viewingAsset.specifications || '-'}
              </Col>
              <Col span={12}>
                <strong>院系归属：</strong>{viewingAsset.department}
              </Col>
              <Col span={12}>
                <strong>采购价格：</strong>{viewingAsset.purchase_price ? `¥${viewingAsset.purchase_price}` : '-'}
              </Col>
              <Col span={12}>
                <strong>购买日期：</strong>{viewingAsset.purchase_date || '-'}
              </Col>
              <Col span={12}>
                <strong>资产现状：</strong>
                <Tag color={AssetStatusColor[viewingAsset.current_status]}>
                  {AssetStatusLabel[viewingAsset.current_status]}
                </Tag>
              </Col>
              <Col span={12}>
                <strong>存放位置：</strong>{viewingAsset.location}
              </Col>
              <Col span={12}>
                <strong>课题组保管人：</strong>{viewingAsset.custodian_name}
              </Col>
              <Col span={12}>
                <strong>保管人电话：</strong>{viewingAsset.custodian_phone || '-'}
              </Col>
              <Col span={12}>
                <strong>资产管理人：</strong>{viewingAsset.manager?.username || '-'}
              </Col>
              {/* 资产照片 - 始终显示三个位置，保持对齐 */}
              <Col span={24} style={{ marginTop: 8 }}>
                <div style={{ marginBottom: 8, fontWeight: 500 }}>资产照片：</div>
                <Row gutter={12}>
                  <Col span={8}>
                    <div style={{
                      border: '1px solid #d9d9d9',
                      borderRadius: 6,
                      padding: 8,
                      textAlign: 'center',
                      minHeight: 120,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <div style={{ fontSize: 12, color: '#666', marginBottom: 8 }}>资产全貌</div>
                      {viewingAsset.photo_full_url ? (
                        <Image
                          width={120}
                          height={120}
                          src={getImageUrl(viewingAsset.photo_full_url)}
                          style={{ objectFit: 'cover' }}
                        />
                      ) : (
                        <div style={{
                          color: '#bfbfbf',
                          fontSize: 48,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          -
                        </div>
                      )}
                    </div>
                  </Col>
                  <Col span={8}>
                    <div style={{
                      border: '1px solid #d9d9d9',
                      borderRadius: 6,
                      padding: 8,
                      textAlign: 'center',
                      minHeight: 120,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <div style={{ fontSize: 12, color: '#666', marginBottom: 8 }}>型号铭牌</div>
                      {viewingAsset.photo_model_url ? (
                        <Image
                          width={120}
                          height={120}
                          src={getImageUrl(viewingAsset.photo_model_url)}
                          style={{ objectFit: 'cover' }}
                        />
                      ) : (
                        <div style={{
                          color: '#bfbfbf',
                          fontSize: 48,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          -
                        </div>
                      )}
                    </div>
                  </Col>
                  <Col span={8}>
                    <div style={{
                      border: '1px solid #d9d9d9',
                      borderRadius: 6,
                      padding:  8,
                      textAlign: 'center',
                      minHeight: 120,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <div style={{ fontSize: 12, color: '#666', marginBottom: 8 }}>固定资产铭牌</div>
                      {viewingAsset.photo_tag_url ? (
                        <Image
                          width={120}
                          height={120}
                          src={getImageUrl(viewingAsset.photo_tag_url)}
                          style={{ objectFit: 'cover' }}
                        />
                      ) : (
                        <div style={{
                          color: '#bfbfbf',
                          fontSize: 48,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          -
                        </div>
                      )}
                    </div>
                  </Col>
                </Row>
              </Col>
              <Col span={24}>
                <strong>备注：</strong>{viewingAsset.remarks || '-'}
              </Col>
            </Row>
          </Card>
        )}
      </Modal>

      {/* 全屏加载遮罩 */}
      {detailLoading && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(255, 255, 255, 0.7)',
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column',
          gap: 16
        }}>
          <Spin size="large" />
          <div style={{ color: '#666', fontSize: 14 }}>加载中...</div>
        </div>
      )}
    </div>
  );
};

export default Assets;

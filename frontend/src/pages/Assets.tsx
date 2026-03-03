import React, { useEffect, useState } from 'react';
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
  Col
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import type { FormInstance } from 'antd/es/form';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  SearchOutlined
} from '@ant-design/icons';
import { getAssets, createAsset, updateAsset, deleteAsset } from '../api/assets';
import { getCategories } from '../api/categories';
import { getSuppliers } from '../api/suppliers';
import { useAuth } from '../contexts/AuthContext';
import type { Asset, Category, Supplier, AssetFormData, QueryParams } from '../types';
import '../styles/common.scss';

const { Option } = Select;
const { TextArea } = Input;

interface AssetFormValues {
  name: string;
  code: string;
  category_id: number;
  supplier_id?: number;
  specifications?: string;
  purchase_date?: Dayjs | null;
  purchase_price?: number;
  location?: string;
  custodian?: string;
  remarks?: string;
}

const Assets: React.FC = () => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [viewModalVisible, setViewModalVisible] = useState(false);
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null);
  const [viewingAsset, setViewingAsset] = useState<Asset | null>(null);
  const [filters, setFilters] = useState<QueryParams>({});
  const [form] = Form.useForm<AssetFormValues>();
  const { isAdmin } = useAuth();

  useEffect(() => {
    fetchAssets();
    fetchCategories();
    fetchSuppliers();
  }, []);

  const fetchAssets = async (params?: QueryParams) => {
    setLoading(true);
    try {
      // Remove undefined, empty string, and false values from params
      const cleanParams: QueryParams = { ...(params || filters) };
      (Object.keys(cleanParams) as Array<keyof QueryParams>).forEach(key => {
        if (cleanParams[key] === undefined || cleanParams[key] === '' || cleanParams[key] === false) {
          delete cleanParams[key];
        }
      });
      const response = await getAssets(cleanParams);
      setAssets(response.data.items || []);
    } catch (error) {
      message.error('获取资产列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await getCategories();
      setCategories(response.data.items || []);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
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
    setEditingAsset(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: Asset) => {
    setEditingAsset(record);
    form.setFieldsValue({
      ...record,
      category_id: record.category?.id,
      supplier_id: record.supplier?.id,
      custodian: record.custodian,
      purchase_date: record.purchase_date ? dayjs(record.purchase_date) : null,
    });
    setModalVisible(true);
  };

  const handleView = (record: Asset) => {
    setViewingAsset(record);
    setViewModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteAsset(id);
      message.success('删除成功');
      fetchAssets();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async (values: AssetFormValues) => {
    try {
      const data: AssetFormData = {
        name: values.name,
        code: values.code,
        category_id: values.category_id,
        supplier_id: values.supplier_id,
        specifications: values.specifications,
        purchase_date: values.purchase_date ? values.purchase_date.format('YYYY-MM-DD') : undefined,
        purchase_price: values.purchase_price,
        location: values.location,
        custodian: values.custodian,
        remarks: values.remarks,
      };

      if (editingAsset) {
        await updateAsset(editingAsset.id, data);
        message.success('更新成功');
      } else {
        await createAsset(data);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchAssets();
    } catch (error) {
      message.error(editingAsset ? '更新失败' : '创建失败');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      available: 'green',
      in_use: 'blue',
      maintenance: 'orange',
      retired: 'red',
    };
    return colors[status] || 'default';
  };

  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      available: '可用',
      in_use: '使用中',
      maintenance: '维修中',
      retired: '已报废',
    };
    return texts[status] || status;
  };

  const columns: ColumnsType<Asset> = [
    {
      title: '资产编号',
      dataIndex: 'code',
      key: 'code',
      width: 120,
    },
    {
      title: '资产名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '类别',
      dataIndex: ['category', 'name'],
      key: 'category',
    },
    {
      title: '供应商',
      dataIndex: ['supplier', 'name'],
      key: 'supplier',
      render: (supplier?: string) => supplier || '-',
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
      title: '存放位置',
      dataIndex: 'location',
      key: 'location',
    },
    {
      title: '保管人',
      dataIndex: 'custodian',
      key: 'custodian',
      render: (custodian?: string) => custodian || '-',
    },
    {
      title: '采购日期',
      dataIndex: 'purchase_date',
      key: 'purchase_date',
    },
    {
      title: '采购价格',
      dataIndex: 'purchase_price',
      key: 'purchase_price',
      render: (price?: number) => price ? `¥${price.toFixed(2)}` : '-',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Asset) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
          >
            查看
          </Button>
          {isAdmin && (
            <>
              <Button
                type="link"
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
                <Button type="link" danger icon={<DeleteOutlined />}>
                  删除
                </Button>
              </Popconfirm>
            </>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">资产管理</h2>
        <Space className="page-actions">
          <Select
            placeholder="按类别筛选"
            style={{ width: 150 }}
            allowClear
            onChange={(value) => {
              const newFilters = { ...filters, category_id: value };
              setFilters(newFilters);
              fetchAssets(newFilters);
            }}
          >
            {categories.map(cat => (
              <Option key={cat.id} value={cat.id}>{cat.name}</Option>
            ))}
          </Select>
          <Select
            placeholder="按状态筛选"
            style={{ width: 120 }}
            allowClear
            onChange={(value) => {
              const newFilters = { ...filters, status: value };
              setFilters(newFilters);
              fetchAssets(newFilters);
            }}
          >
            <Option value="available">可用</Option>
            <Option value="in_use">使用中</Option>
            <Option value="maintenance">维修中</Option>
            <Option value="retired">已报废</Option>
          </Select>
          {isAdmin && (
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              添加资产
            </Button>
          )}
        </Space>
      </div>

      <div className="table-container">
        <Table
          columns={columns}
          dataSource={assets}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </div>

      <Modal
        title={editingAsset ? '编辑资产' : '添加资产'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={800}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
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
                name="code"
                label="资产编号"
                rules={[{ required: true, message: '请输入资产编号' }]}
              >
                <Input placeholder="请输入资产编号" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="category_id"
                label="资产类别"
                rules={[{ required: true, message: '请选择资产类别' }]}
              >
                <Select placeholder="请选择资产类别">
                  {categories.map(cat => (
                    <Option key={cat.id} value={cat.id}>{cat.name}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="supplier_id" label="供应商">
                <Select placeholder="请选择供应商" allowClear>
                  {suppliers.map(sup => (
                    <Option key={sup.id} value={sup.id}>{sup.name}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="specifications" label="规格参数">
            <TextArea rows={3} placeholder="请输入规格参数" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="purchase_date" label="采购日期">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
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
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="location" label="存放位置">
                <Input placeholder="请输入存放位置" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="custodian" label="保管人（可选）">
                <Input placeholder="请输入保管人姓名" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="remarks" label="备注">
            <TextArea rows={3} placeholder="请输入备注" />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingAsset ? '更新' : '创建'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="资产详情"
        open={viewModalVisible}
        onCancel={() => setViewModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setViewModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={800}
      >
        {viewingAsset && (
          <Card>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <strong>资产编号：</strong>{viewingAsset.code}
              </Col>
              <Col span={12}>
                <strong>资产名称：</strong>{viewingAsset.name}
              </Col>
              <Col span={12}>
                <strong>类别：</strong>{viewingAsset.category?.name}
              </Col>
              <Col span={12}>
                <strong>状态：</strong>
                <Tag color={getStatusColor(viewingAsset.status)}>
                  {getStatusText(viewingAsset.status)}
                </Tag>
              </Col>
              <Col span={12}>
                <strong>供应商：</strong>{viewingAsset.supplier?.name || '-'}
              </Col>
              <Col span={12}>
                <strong>存放位置：</strong>{viewingAsset.location || '-'}
              </Col>
              <Col span={12}>
                <strong>保管人：</strong>{viewingAsset.custodian || '-'}
              </Col>
              <Col span={12}>
                <strong>采购日期：</strong>{viewingAsset.purchase_date || '-'}
              </Col>
              <Col span={12}>
                <strong>采购价格：</strong>{viewingAsset.purchase_price ? `¥${viewingAsset.purchase_price.toFixed(2)}` : '-'}
              </Col>
              <Col span={24}>
                <strong>规格参数：</strong>{viewingAsset.specifications || '-'}
              </Col>
              <Col span={24}>
                <strong>备注：</strong>{viewingAsset.remarks || '-'}
              </Col>
            </Row>
          </Card>
        )}
      </Modal>
    </div>
  );
};

export default Assets;

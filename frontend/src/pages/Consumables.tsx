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
  Popconfirm,
  Tag,
  Card,
  Row,
  Col,
  Alert
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  WarningOutlined
} from '@ant-design/icons';
import { getConsumables, createConsumable, updateConsumable, deleteConsumable } from '../api/consumables';
import { getCategories } from '../api/categories';
import { getSuppliers } from '../api/suppliers';
import { useAuth } from '../contexts/AuthContext';
import type { Consumable, Category, Supplier, ConsumableFormData, QueryParams } from '../types';
import '../styles/common.scss';

const { Option } = Select;
const { TextArea } = Input;

const Consumables: React.FC = () => {
  const [consumables, setConsumables] = useState<Consumable[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [viewModalVisible, setViewModalVisible] = useState(false);
  const [editingConsumable, setEditingConsumable] = useState<Consumable | null>(null);
  const [viewingConsumable, setViewingConsumable] = useState<Consumable | null>(null);
  const [filters, setFilters] = useState<QueryParams>({});
  const [form] = Form.useForm<ConsumableFormData>();
  const { isAdmin } = useAuth();

  useEffect(() => {
    fetchConsumables();
    fetchCategories();
    fetchSuppliers();
  }, []);

  const fetchConsumables = async (params?: QueryParams) => {
    setLoading(true);
    try {
      // Remove undefined, empty string, and false values from params
      const cleanParams: QueryParams = { ...(params || filters) };
      (Object.keys(cleanParams) as Array<keyof QueryParams>).forEach(key => {
        if (cleanParams[key] === undefined || cleanParams[key] === '' || cleanParams[key] === false) {
          delete cleanParams[key];
        }
      });
      const response = await getConsumables(cleanParams);
      setConsumables(response.data.items || []);
    } catch (error) {
      message.error('获取耗材列表失败');
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
    setEditingConsumable(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: Consumable) => {
    setEditingConsumable(record);
    form.setFieldsValue({
      ...record,
      category_id: record.category?.id,
      supplier_id: record.supplier?.id,
    });
    setModalVisible(true);
  };

  const handleView = (record: Consumable) => {
    setViewingConsumable(record);
    setViewModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteConsumable(id);
      message.success('删除成功');
      fetchConsumables();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async (values: ConsumableFormData) => {
    try {
      if (editingConsumable) {
        await updateConsumable(editingConsumable.id, values);
        message.success('更新成功');
      } else {
        await createConsumable(values);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchConsumables();
    } catch (error) {
      message.error(editingConsumable ? '更新失败' : '创建失败');
    }
  };

  const columns: ColumnsType<Consumable> = [
    {
      title: '耗材编号',
      dataIndex: 'code',
      key: 'code',
      width: 120,
    },
    {
      title: '耗材名称',
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
      title: '单位',
      dataIndex: 'unit',
      key: 'unit',
      width: 80,
    },
    {
      title: '当前库存',
      dataIndex: 'stock',
      key: 'stock',
      render: (stock: number, record: Consumable) => (
        <Tag color={stock < record.min_stock ? 'red' : 'green'}>
          {stock} {record.unit}
        </Tag>
      ),
    },
    {
      title: '最低库存',
      dataIndex: 'min_stock',
      key: 'min_stock',
      render: (min_stock: number) => `${min_stock}`,
    },
    {
      title: '单价',
      dataIndex: 'price',
      key: 'price',
      render: (price?: number) => price ? `¥${price.toFixed(2)}` : '-',
    },
    {
      title: '存放位置',
      dataIndex: 'location',
      key: 'location',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Consumable) => (
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
                title="确定要删除这个耗材吗？"
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
        <h2 className="page-title">耗材管理</h2>
        <Space className="page-actions">
          <Select
            placeholder="按类别筛选"
            style={{ width: 150 }}
            allowClear
            onChange={(value) => {
              const newFilters = { ...filters, category_id: value };
              setFilters(newFilters);
              fetchConsumables(newFilters);
            }}
          >
            {categories.map(cat => (
              <Option key={cat.id} value={cat.id}>{cat.name}</Option>
            ))}
          </Select>
          <Button
            type={filters.low_stock ? 'primary' : 'default'}
            icon={<WarningOutlined />}
            onClick={() => {
              const newFilters = { ...filters, low_stock: !filters.low_stock };
              setFilters(newFilters);
              fetchConsumables(newFilters);
            }}
          >
            {filters.low_stock ? '显示全部' : '仅显示低库存'}
          </Button>
          {isAdmin && (
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              添加耗材
            </Button>
          )}
        </Space>
      </div>

      {filters.low_stock && (
        <Alert
          message="仅显示库存低于最低库存的耗材"
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <div className="table-container">
        <Table
          columns={columns}
          dataSource={consumables}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </div>

      <Modal
        title={editingConsumable ? '编辑耗材' : '添加耗材'}
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
                label="耗材名称"
                rules={[{ required: true, message: '请输入耗材名称' }]}
              >
                <Input placeholder="请输入耗材名称" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="category_id"
                label="耗材类别"
                rules={[{ required: true, message: '请选择耗材类别' }]}
              >
                <Select placeholder="请选择耗材类别">
                  {categories.map(cat => (
                    <Option key={cat.id} value={cat.id}>{cat.name}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="supplier_id" label="供应商">
                <Select placeholder="请选择供应商" allowClear>
                  {suppliers.map(sup => (
                    <Option key={sup.id} value={sup.id}>{sup.name}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="unit"
                label="单位"
                rules={[{ required: true, message: '请输入单位' }]}
                initialValue="个"
              >
                <Input placeholder="请输入单位" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="stock"
                label="初始库存"
                rules={[{ required: true, message: '请输入初始库存' }]}
                initialValue={0}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="请输入初始库存"
                  min={0}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="min_stock"
                label="最低库存"
                rules={[{ required: true, message: '请输入最低库存' }]}
                initialValue={10}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="请输入最低库存"
                  min={0}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="price" label="单价">
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="请输入单价"
                  min={0}
                  precision={2}
                  prefix="¥"
                />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="location" label="存放位置">
            <Input placeholder="请输入存放位置" />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingConsumable ? '更新' : '创建'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="耗材详情"
        open={viewModalVisible}
        onCancel={() => setViewModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setViewModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={800}
      >
        {viewingConsumable && (
          <Card>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <strong>耗材编号：</strong>{viewingConsumable.code}
              </Col>
              <Col span={12}>
                <strong>耗材名称：</strong>{viewingConsumable.name}
              </Col>
              <Col span={12}>
                <strong>类别：</strong>{viewingConsumable.category?.name}
              </Col>
              <Col span={12}>
                <strong>单位：</strong>{viewingConsumable.unit}
              </Col>
              <Col span={12}>
                <strong>当前库存：</strong>
                <Tag color={viewingConsumable.stock < viewingConsumable.min_stock ? 'red' : 'green'}>
                  {viewingConsumable.stock} {viewingConsumable.unit}
                </Tag>
              </Col>
              <Col span={12}>
                <strong>最低库存：</strong>{viewingConsumable.min_stock} {viewingConsumable.unit}
              </Col>
              <Col span={12}>
                <strong>供应商：</strong>{viewingConsumable.supplier?.name || '-'}
              </Col>
              <Col span={12}>
                <strong>单价：</strong>{viewingConsumable.price ? `¥${viewingConsumable.price.toFixed(2)}` : '-'}
              </Col>
              <Col span={12}>
                <strong>存放位置：</strong>{viewingConsumable.location || '-'}
              </Col>
            </Row>
          </Card>
        )}
      </Modal>
    </div>
  );
};

export default Consumables;

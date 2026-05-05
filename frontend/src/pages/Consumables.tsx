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
import { getConsumables, createConsumable, updateConsumable, deleteConsumable, ConsumableTypeLabels, ConsumableFormLabels } from '../api/consumables';
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
      production_date: record.production_date ? dayjs(record.production_date) : null,
      expiration_date: record.expiration_date ? dayjs(record.expiration_date) : null,
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
    } catch (error: any) {
      const errorMsg = error?.message || '删除失败';
      message.error(errorMsg);
    }
  };

  const handleSubmit = async (values: ConsumableFormData) => {
    try {
      const data = {
        ...values,
        production_date: values.production_date ? dayjs(values.production_date).format('YYYY-MM-DD') : undefined,
        expiration_date: values.expiration_date ? dayjs(values.expiration_date).format('YYYY-MM-DD') : undefined,
      };
      if (editingConsumable) {
        await updateConsumable(editingConsumable.id, data);
        message.success('更新成功');
      } else {
        await createConsumable(data);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchConsumables();
    } catch (error: any) {
      const errorMsg = error?.message || (editingConsumable ? '更新失败' : '创建失败');
      message.error(errorMsg);
    }
  };

  const columns: ColumnsType<Consumable> = [
    {
      title: '序号',
      key: 'index',
      width: 60,
      render: (_: any, __: Consumable, index: number) => index + 1,
    },
    {
      title: '耗材编号',
      dataIndex: 'code',
      key: 'code',
      width: 100,
    },
    {
      title: '产品名称',
      dataIndex: 'name',
      key: 'name',
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
      title: 'CAS号',
      dataIndex: 'cas_number',
      key: 'cas_number',
      width: 100,
      render: (cas?: string) => cas || '-',
    },
    {
      title: '形态',
      dataIndex: 'form',
      key: 'form',
      width: 80,
      render: (form?: string) => form ? ConsumableFormLabels[form] : '-',
    },
    {
      title: '分类',
      dataIndex: 'consumable_type',
      key: 'consumable_type',
      width: 80,
      render: (type: string) => (
        <Tag color={type === 'reagent' ? 'blue' : 'green'}>
          {ConsumableTypeLabels[type]}
        </Tag>
      ),
    },
    {
      title: '是否危化品',
      dataIndex: 'is_hazardous',
      key: 'is_hazardous',
      width: 100,
      render: (isHazardous: boolean) => (
        <Tag color={isHazardous ? 'red' : 'default'}>
          {isHazardous ? '是' : '否'}
        </Tag>
      ),
    },
    {
      title: '规格',
      dataIndex: 'specifications',
      key: 'specifications',
      width: 100,
      render: (spec?: string) => spec || '-',
    },
    {
      title: '现存数量',
      dataIndex: 'stock',
      key: 'stock',
      width: 100,
      render: (stock: number, record: Consumable) => (
        <Tag color={stock < record.min_stock ? 'red' : 'green'}>
          {stock}
        </Tag>
      ),
    },
    {
      title: '课题组保管人',
      dataIndex: 'custodian_name',
      key: 'custodian_name',
      width: 120,
    },
    {
      title: '是否过期',
      dataIndex: 'is_expired',
      key: 'is_expired',
      width: 100,
      render: (isExpired?: boolean) => (
        <Tag color={isExpired ? 'red' : 'green'}>
          {isExpired ? '已过期' : '未过期'}
        </Tag>
      ),
    },
    {
      title: '存放位置',
      key: 'location',
      width: 150,
      render: (_: any, record: Consumable) => {
        const parts = [record.campus, record.building, record.room, record.storage_area].filter(Boolean);
        return parts.join('/') || '-';
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      fixed: 'right' as const,
      render: (_: any, record: Consumable) => (
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
                title="确定要删除这个耗材吗？"
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

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">耗材管理</h2>
        <Space className="page-actions">
          <Select
            placeholder="按类别筛选"
            style={{ width: 120 }}
            allowClear
            onChange={(value) => {
              const newFilters = { ...filters, consumable_type: value };
              setFilters(newFilters);
              fetchConsumables(newFilters);
            }}
          >
            <Option value="consumable">耗材</Option>
            <Option value="reagent">试剂</Option>
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
          <Button
            type={filters.is_expired ? 'primary' : 'default'}
            onClick={() => {
              const newFilters = { ...filters, is_expired: !filters.is_expired };
              setFilters(newFilters);
              fetchConsumables(newFilters);
            }}
          >
            {filters.is_expired ? '显示全部' : '仅显示过期'}
          </Button>
          {isAdmin && (
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              添加耗材
            </Button>
          )}
        </Space>
      </div>

      {(filters.low_stock || filters.is_expired) && (
        <Alert
          message={filters.low_stock ? '仅显示库存低于最低库存的耗材' : '仅显示已过期的耗材'}
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
          scroll={{ x: 2000 }}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </div>

      {/* 添加/编辑耗材模态框 */}
      <Modal
        title={editingConsumable ? '编辑耗材' : '添加耗材'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={900}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Card title="基本信息" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="name"
                  label="产品名称"
                  rules={[{ required: true, message: '请输入产品名称' }]}
                >
                  <Input placeholder="请输入产品名称" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="category_id"
                  label="类别"
                  rules={[{ required: true, message: '请选择类别' }]}
                >
                  <Select placeholder="请选择类别">
                    {categories.map(cat => (
                      <Option key={cat.id} value={cat.id}>{cat.name}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={8}>
                <Form.Item name="brand" label="品牌">
                  <Input placeholder="请输入品牌" />
                </Form.Item>
              </Col>
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
            </Row>
            <Row gutter={16}>
              <Col span={8}>
                <Form.Item name="form" label="形态">
                  <Select placeholder="请选择形态">
                    <Option value="solid">固体</Option>
                    <Option value="liquid">液体</Option>
                    <Option value="gas">气体</Option>
                  </Select>
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  name="consumable_type"
                  label="分类"
                  initialValue="consumable"
                >
                  <Select>
                    <Option value="consumable">耗材</Option>
                    <Option value="reagent">试剂</Option>
                  </Select>
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  name="is_hazardous"
                  label="是否危化品"
                  valuePropName="checked"
                >
                  <Select>
                    <Option value={false}>否</Option>
                    <Option value={true}>是</Option>
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
                <Form.Item name="supplier_id" label="供应商">
                  <Select placeholder="请选择供应商" allowClear>
                    {suppliers.map(sup => (
                      <Option key={sup.id} value={sup.id}>{sup.name}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>
          </Card>

          <Card title="库存信息" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={8}>
                <Form.Item
                  name="stock"
                  label="现存数量"
                  rules={[{ required: true, message: '请输入现存数量' }]}
                  initialValue={0}
                >
                  <InputNumber
                    style={{ width: '100%' }}
                    placeholder="请输入现存数量"
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
          </Card>

          <Card title="保管人信息" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="custodian_name"
                  label="课题组保管人"
                  rules={[{ required: true, message: '请输入保管人' }]}
                >
                  <Input placeholder="请输入保管人" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="custodian_phone"
                  label="保管人联系方式"
                  rules={[{ required: true, message: '请输入联系方式' }]}
                >
                  <Input placeholder="请输入联系方式" />
                </Form.Item>
              </Col>
            </Row>
          </Card>

          <Card title="日期信息" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="production_date" label="产品最早生产日期">
                  <DatePicker style={{ width: '100%' }} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="expiration_date" label="产品保质期">
                  <DatePicker style={{ width: '100%' }} />
                </Form.Item>
              </Col>
            </Row>
          </Card>

          <Card title="存放信息" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={6}>
                <Form.Item name="campus" label="存放校区">
                  <Input placeholder="请输入校区" />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item name="building" label="存放楼宇">
                  <Input placeholder="请输入楼宇" />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item name="room" label="存放房间">
                  <Input placeholder="请输入房间" />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item name="storage_area" label="存放区域">
                  <Input placeholder="请输入区域" />
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
                {editingConsumable ? '更新' : '创建'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 查看耗材详情模态框 */}
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
                <strong>产品名称：</strong>{viewingConsumable.name}
              </Col>
              <Col span={12}>
                <strong>品牌：</strong>{viewingConsumable.brand || '-'}
              </Col>
              <Col span={12}>
                <strong>货号：</strong>{viewingConsumable.product_code}
              </Col>
              <Col span={12}>
                <strong>CAS号：</strong>{viewingConsumable.cas_number || '-'}
              </Col>
              <Col span={12}>
                <strong>形态：</strong>{viewingConsumable.form ? ConsumableFormLabels[viewingConsumable.form] : '-'}
              </Col>
              <Col span={12}>
                <strong>分类：</strong>
                <Tag color={viewingConsumable.consumable_type === 'reagent' ? 'blue' : 'green'}>
                  {ConsumableTypeLabels[viewingConsumable.consumable_type]}
                </Tag>
              </Col>
              <Col span={12}>
                <strong>是否危化品：</strong>
                <Tag color={viewingConsumable.is_hazardous ? 'red' : 'default'}>
                  {viewingConsumable.is_hazardous ? '是' : '否'}
                </Tag>
              </Col>
              <Col span={12}>
                <strong>规格：</strong>{viewingConsumable.specifications || '-'}
              </Col>
              <Col span={12}>
                <strong>现存数量：</strong>
                <Tag color={viewingConsumable.stock < viewingConsumable.min_stock ? 'red' : 'green'}>
                  {viewingConsumable.stock}
                </Tag>
              </Col>
              <Col span={12}>
                <strong>最低库存：</strong>{viewingConsumable.min_stock}
              </Col>
              <Col span={12}>
                <strong>课题组保管人：</strong>{viewingConsumable.custodian_name}
              </Col>
              <Col span={12}>
                <strong>保管人联系方式：</strong>{viewingConsumable.custodian_phone}
              </Col>
              <Col span={12}>
                <strong>产品最早生产日期：</strong>{viewingConsumable.production_date || '-'}
              </Col>
              <Col span={12}>
                <strong>产品保质期：</strong>{viewingConsumable.expiration_date || '-'}
              </Col>
              <Col span={12}>
                <strong>是否过期：</strong>
                <Tag color={viewingConsumable.is_expired ? 'red' : 'green'}>
                  {viewingConsumable.is_expired ? '已过期' : '未过期'}
                </Tag>
              </Col>
              <Col span={12}>
                <strong>存放位置：</strong>
                {[viewingConsumable.campus, viewingConsumable.building, viewingConsumable.room, viewingConsumable.storage_area]
                  .filter(Boolean).join('/') || '-'}
              </Col>
              <Col span={12}>
                <strong>单价：</strong>{viewingConsumable.price ? `¥${viewingConsumable.price}` : '-'}
              </Col>
              <Col span={24}>
                <strong>备注：</strong>{viewingConsumable.remarks || '-'}
              </Col>
            </Row>
          </Card>
        )}
      </Modal>
    </div>
  );
};

export default Consumables;

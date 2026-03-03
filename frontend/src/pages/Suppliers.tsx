import React, { useEffect, useState } from 'react';
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  message,
  Popconfirm
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined
} from '@ant-design/icons';
import { getSuppliers, createSupplier, updateSupplier, deleteSupplier } from '../api/suppliers';
import { useAuth } from '../contexts/AuthContext';
import type { Supplier } from '../types';
import '../styles/common.scss';

// 供应商管理页面组件（仅管理员可见）
const Suppliers: React.FC = () => {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState<Supplier | null>(null);
  const [form] = Form.useForm<{
    name: string;
    contact?: string;
    phone?: string;
    email?: string;
    address?: string;
  }>();
  const { isAdmin } = useAuth();

  // 初始化加载供应商列表
  useEffect(() => {
    fetchSuppliers();
  }, []);

  // 获取供应商列表
  const fetchSuppliers = async () => {
    setLoading(true);
    try {
      const response = await getSuppliers();
      setSuppliers(response.data.items || []);
    } catch (error) {
      message.error('获取供应商列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 打开添加供应商弹窗
  const handleAdd = () => {
    setEditingSupplier(null);
    form.resetFields();
    setModalVisible(true);
  };

  // 打开编辑供应商弹窗
  const handleEdit = (record: Supplier) => {
    setEditingSupplier(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  // 删除供应商
  const handleDelete = async (id: number) => {
    try {
      await deleteSupplier(id);
      message.success('删除成功');
      fetchSuppliers();
    } catch (error) {
      message.error('删除失败');
    }
  };

  // 提交供应商表单
  const handleSubmit = async (values: {
    name: string;
    contact?: string;
    phone?: string;
    email?: string;
    address?: string;
  }) => {
    try {
      if (editingSupplier) {
        await updateSupplier(editingSupplier.id, values);
        message.success('更新成功');
      } else {
        await createSupplier(values);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchSuppliers();
    } catch (error) {
      message.error(editingSupplier ? '更新失败' : '创建失败');
    }
  };

  // 表格列定义
  const columns: ColumnsType<Supplier> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '供应商名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '联系人',
      dataIndex: 'contact',
      key: 'contact',
      render: (contact?: string) => contact || '-',
    },
    {
      title: '电话',
      dataIndex: 'phone',
      key: 'phone',
      render: (phone?: string) => phone || '-',
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      render: (email?: string) => email || '-',
    },
    {
      title: '地址',
      dataIndex: 'address',
      key: 'address',
      render: (address?: string) => address || '-',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Supplier) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个供应商吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">供应商管理</h2>
        {isAdmin && (
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            添加供应商
          </Button>
        )}
      </div>

      <div className="table-container">
        <Table
          columns={columns}
          dataSource={suppliers}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </div>

      <Modal
        title={editingSupplier ? '编辑供应商' : '添加供应商'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="name"
            label="供应商名称"
            rules={[{ required: true, message: '请输入供应商名称' }]}
          >
            <Input placeholder="请输入供应商名称" />
          </Form.Item>
          <Form.Item name="contact" label="联系人">
            <Input placeholder="请输入联系人" />
          </Form.Item>
          <Form.Item name="phone" label="电话">
            <Input placeholder="请输入电话" />
          </Form.Item>
          <Form.Item name="email" label="邮箱">
            <Input placeholder="请输入邮箱" />
          </Form.Item>
          <Form.Item name="address" label="地址">
            <Input.TextArea rows={3} placeholder="请输入地址" />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingSupplier ? '更新' : '创建'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Suppliers;

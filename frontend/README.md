# 课题组资产管理系统 - 前端

基于 React 18 + Ant Design + Vite 构建的课题组资产管理系统前端应用。

## 技术栈

- **React 18** - 用户界面库
- **Vite** - 构建工具
- **Ant Design 5** - UI 组件库
- **React Router 6** - 路由管理
- **Axios** - HTTP 客户端
- **Day.js** - 日期处理

## 功能模块

### 1. 用户认证
- 用户注册
- 用户登录
- 用户登出
- JWT 认证

### 2. 仪表盘
- 资产总数统计
- 耗材总数统计
- 我的借用中数量
- 我的采购申请数量
- 低库存耗材预警
- 管理员专属统计（待审批数量）

### 3. 资产管理
- 资产列表查看
- 资产详情查看
- 添加资产（管理员）
- 编辑资产（管理员）
- 删除资产（管理员）
- 按类别/状态筛选

### 4. 耗材管理
- 耗材列表查看
- 耗材详情查看
- 添加耗材（管理员）
- 编辑耗材（管理员）
- 删除耗材（管理员）
- 按类别筛选
- 低库存预警

### 5. 采购管理
- 提交采购申请
- 查看我的采购申请
- 审批采购申请（管理员）
- 查看采购申请详情

### 6. 资产借用
- 借用可用资产
- 归还已借用的资产
- 查看我的借用记录
- 查看借用记录详情

### 7. 领料管理
- 提交领料申请
- 查看我的领料记录
- 审批领料申请（管理员）
- 查看领料记录详情

### 8. 资产转移
- 提交资产转移申请
- 查看我的转移申请
- 审批转移申请（管理员）
- 查看转移申请详情

### 9. 统计分析
- 资产按状态统计
- 资产按类别统计
- 耗材总价值
- 低库存耗材数量
- 采购申请按状态统计
- 采购总预算
- 当前借用中数量

### 10. 操作日志
- 查看系统操作日志（管理员）
- 操作人、操作类型、操作对象、操作时间

### 11. 基础数据管理
- 资产类别管理（管理员）
- 供应商管理（管理员）

### 12. 帮助文档
- 系统简介
- 功能模块说明
- 操作指南
- 常见问题解答

## 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── api/               # API 接口
│   │   ├── index.js       # Axios 实例配置
│   │   ├── auth.js        # 认证接口
│   │   ├── assets.js      # 资产接口
│   │   ├── consumables.js # 耗材接口
│   │   ├── purchases.js   # 采购接口
│   │   ├── borrows.js     # 借用接口
│   │   ├── picks.js       # 领料接口
│   │   ├── transfers.js   # 转移接口
│   │   ├── dashboard.js   # 仪表盘接口
│   │   ├── statistics.js  # 统计接口
│   │   ├── logs.js       # 日志接口
│   │   ├── categories.js  # 类别接口
│   │   └── suppliers.js  # 供应商接口
│   ├── components/        # 公共组件
│   │   ├── Layout.jsx     # 主布局
│   │   └── ProtectedRoute.jsx # 路由保护
│   ├── contexts/          # React Context
│   │   └── AuthContext.jsx # 认证上下文
│   ├── pages/            # 页面组件
│   │   ├── Login.jsx      # 登录/注册页
│   │   ├── Dashboard.jsx  # 仪表盘
│   │   ├── Assets.jsx     # 资产管理
│   │   ├── Consumables.jsx # 耗材管理
│   │   ├── Purchases.jsx  # 采购管理
│   │   ├── Borrows.jsx    # 资产借用
│   │   ├── Picks.jsx      # 领料管理
│   │   ├── Transfers.jsx  # 资产转移
│   │   ├── Statistics.jsx # 统计分析
│   │   ├── Logs.jsx       # 操作日志
│   │   ├── Categories.jsx # 类别管理
│   │   ├── Suppliers.jsx  # 供应商管理
│   │   └── Help.jsx       # 帮助文档
│   ├── App.jsx           # 应用根组件
│   ├── main.jsx          # 应用入口
│   └── index.css         # 全局样式
├── .env.example          # 环境变量示例
├── package.json          # 项目依赖
└── vite.config.js        # Vite 配置
```

## 安装依赖

```bash
npm install
```

## 环境配置

复制 `.env.example` 为 `.env` 并配置后端 API 地址：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
VITE_API_BASE_URL=http://localhost:5000/api
```

## 开发

```bash
npm run dev
```

应用将在 `http://localhost:5173` 启动。

## 构建

```bash
npm run build
```

构建产物将输出到 `dist` 目录。

## 预览构建

```bash
npm run preview
```

## 用户角色

### 普通用户
- 查看资产和耗材列表
- 提交采购/领料/转移申请
- 借用和归还资产
- 查看自己的申请和借用记录
- 查看统计数据

### 管理员
- 所有普通用户权限
- 审批采购/领料/转移申请
- 添加/编辑/删除资产和耗材
- 管理资产类别和供应商
- 查看操作日志

## API 接口

所有 API 请求都通过 `src/api/` 目录下的模块进行，使用 Axios 实例自动添加 JWT token。

### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

### 资产接口
- `GET /api/assets` - 获取资产列表
- `GET /api/assets/:id` - 获取资产详情
- `POST /api/assets` - 创建资产（管理员）
- `PUT /api/assets/:id` - 更新资产（管理员）
- `DELETE /api/assets/:id` - 删除资产（管理员）

### 耗材接口
- `GET /api/consumables` - 获取耗材列表
- `GET /api/consumables/:id` - 获取耗材详情
- `POST /api/consumables` - 创建耗材（管理员）
- `PUT /api/consumables/:id` - 更新耗材（管理员）
- `DELETE /api/consumables/:id` - 删除耗材（管理员）

### 采购接口
- `GET /api/purchases` - 获取采购申请列表
- `POST /api/purchases` - 创建采购申请
- `POST /api/purchases/:id/approve` - 审批采购申请（管理员）

### 借用接口
- `POST /api/borrows` - 借用资产
- `POST /api/borrows/:id/return` - 归还资产
- `GET /api/borrows/my` - 获取我的借用记录

### 领料接口
- `GET /api/picks` - 获取领料记录列表
- `POST /api/picks` - 创建领料申请
- `POST /api/picks/:id/approve` - 审批领料申请（管理员）

### 转移接口
- `GET /api/transfers` - 获取转移申请列表
- `POST /api/transfers` - 创建转移申请
- `POST /api/transfers/:id/approve` - 审批转移申请（管理员）

### 统计接口
- `GET /api/dashboard` - 获取仪表盘数据
- `GET /api/statistics` - 获取统计数据

### 日志接口
- `GET /api/logs` - 获取操作日志（管理员）

### 基础数据接口
- `GET /api/categories` - 获取类别列表
- `POST /api/categories` - 创建类别（管理员）
- `PUT /api/categories/:id` - 更新类别（管理员）
- `DELETE /api/categories/:id` - 删除类别（管理员）
- `GET /api/suppliers` - 获取供应商列表
- `POST /api/suppliers` - 创建供应商（管理员）
- `PUT /api/suppliers/:id` - 更新供应商（管理员）
- `DELETE /api/suppliers/:id` - 删除供应商（管理员）

## 浏览器支持

- Chrome (最新版)
- Firefox (最新版)
- Edge (最新版)
- Safari (最新版)

## 响应式设计

系统支持以下屏幕尺寸：
- 桌面端（1920x1080 及以上）
- 平板端（768px-1024px）
- 移动端（<768px）

## 注意事项

1. 确保 `.env` 文件中的 `VITE_API_BASE_URL` 配置正确
2. 后端 API 需要支持 CORS
3. JWT token 存储在 localStorage 中
4. 所有需要认证的接口会自动在请求头中添加 `Authorization: Bearer <token>`
5. token 过期时会自动跳转到登录页

## 开发建议

1. 使用 React DevTools 进行调试
2. 使用 Ant Design 组件时参考官方文档
3. 遵循 React Hooks 最佳实践
4. 保持组件单一职责原则
5. 使用 Context API 管理全局状态

## 许可证

MIT

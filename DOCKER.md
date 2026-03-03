# Docker 部署指南

实验室资产管理系统的 Docker 容器化部署说明。

## 目录结构

```
LAB/
├── backend/              # 后端服务
│   ├── Dockerfile       # 后端镜像构建文件
│   └── .dockerignore    # 后端构建忽略文件
├── frontend/            # 前端服务
│   ├── Dockerfile       # 前端镜像构建文件
│   ├── nginx.conf       # 前端 Nginx 配置
│   └── .dockerignore    # 前端构建忽略文件
├── nginx/               # 反向代理配置
│   ├── nginx.conf       # Nginx 主配置
│   └── conf.d/          # 站点配置
│       └── default.conf # 默认站点配置
├── docker-compose.yml        # 开发环境配置（前后端独立端口）
├── docker-compose-prod.yml   # 生产环境配置（Nginx 反向代理）
└── deploy.sh            # 自动部署脚本
```

## 本地快速启动

### 1. 构建并启动所有服务

```bash
docker-compose up -d
```

### 2. 查看服务状态

```bash
docker-compose ps
```

### 3. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend
```

### 4. 停止服务

```bash
docker-compose stop
```

### 5. 停止并删除容器

```bash
docker-compose down
```

### 6. 重新构建镜像

```bash
docker-compose build --no-cache
docker-compose up -d
```

## 服务访问（本地开发）

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | http://localhost | React 前端应用 |
| 后端 API | http://localhost:5000/api | Flask 后端 API |

---

## 服务器部署

### 方式一：使用自动部署脚本（推荐）

1. **修改部署脚本**

编辑 `deploy.sh`，修改服务器信息：

```bash
SERVER_USER="root"           # 服务器用户名
SERVER_HOST="192.168.1.100"  # 服务器 IP 地址
```

2. **执行部署**

```bash
chmod +x deploy.sh
./deploy.sh
```

脚本会自动完成：
- 打包项目文件
- 上传到服务器
- 构建 Docker 镜像
- 启动服务
- 初始化数据库

### 方式二：手动部署

#### 步骤 1：打包项目

```bash
# 在本地执行
tar czf lab-project.tar.gz \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='*.db' \
  --exclude='venv' \
  backend/ frontend/ nginx/ docker-compose-prod.yml
```

#### 步骤 2：上传到服务器

```bash
scp lab-project.tar.gz user@your-server:/tmp/
```

#### 步骤 3：在服务器上解压并部署

```bash
# SSH 登录服务器
ssh user@your-server

# 创建部署目录
mkdir -p /opt/lab-asset-system
cd /opt/lab-asset-system

# 解压文件
tar xzf /tmp/lab-project.tar.gz

# 构建并启动（使用生产配置）
docker-compose -f docker-compose-prod.yml up -d
```

#### 步骤 4：初始化数据库

```bash
# 首次部署需要初始化数据库
docker-compose -f docker-compose-prod.yml exec backend python init_sqlite_db.py
```

---

## API 地址配置说明

### ⚠️ 重要：API 地址需要根据部署方式修改

前端代码中的 API 地址是在**构建时**确定的，因此需要根据实际部署方式修改。

### 本地开发环境

使用 `docker-compose.yml`，前端直接访问后端：

```yaml
frontend:
  args:
    - VITE_API_BASE_URL=http://localhost:5000/api
```

浏览器访问方式：
- 前端: http://localhost
- 后端: http://localhost:5000/api

### 生产环境（推荐）

使用 `docker-compose-prod.yml`，通过 Nginx 反向代理统一入口：

```yaml
frontend:
  args:
    - VITE_API_BASE_URL=/api   # 使用相对路径
```

**部署到服务器后，如果服务器域名是 `example.com`：**

访问方式：
- 前端: http://example.com
- 后端: http://example.com/api

**不需要修改 API 地址**，因为：
- 前端和后端都通过同一个域名访问
- `/api` 请求会被 Nginx 转发到后端容器

### 如果需要修改 API 地址

编辑对应的 docker-compose 文件：

```yaml
frontend:
  build:
    args:
      # 方式1：使用相对路径（推荐，通过反向代理）
      - VITE_API_BASE_URL=/api

      # 方式2：使用完整地址
      - VITE_API_BASE_URL=http://your-domain.com/api

      # 方式3：使用不同端口
      - VITE_API_BASE_URL=http://your-domain.com:8080/api
```

**修改后需要重新构建前端镜像：**

```bash
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

---

## 数据持久化

### 查看数据卷

```bash
docker volume ls
```

### 备份数据

```bash
# 备份到当前目录
docker run --rm -v lab_asset-system_backend-data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz /data
```

### 恢复数据

```bash
docker run --rm -v lab_asset-system_backend-data:/data -v $(pwd):/backup alpine tar xzf /backup/data-backup.tar.gz -C /
```

---

## 常见问题

### 1. 端口冲突

修改 docker-compose.yml 中的端口映射：

```yaml
services:
  nginx:
    ports:
      - "8080:80"   # 使用 8080 端口
```

### 2. 容器无法启动

查看详细日志：

```bash
docker-compose -f docker-compose-prod.yml logs backend
docker-compose -f docker-compose-prod.yml logs frontend
docker-compose -f docker-compose-prod.yml logs nginx
```

### 3. 前端无法访问后端 API

检查项：
1. 后端服务是否正常运行
2. Nginx 配置是否正确
3. 浏览器控制台是否有错误
4. 网络是否连通

```bash
# 检查容器网络
docker network inspect lab_asset-system_lab-network

# 测试 API 连接
docker-compose -f docker-compose-prod.yml exec nginx wget -O- http://backend:5000/api/health
```

### 4. 如何更新部署

```bash
# 上传新代码后
docker-compose -f docker-compose-prod.yml build
docker-compose -f docker-compose-prod.yml up -d
```

---

## HTTPS 配置（可选）

### 使用 Let's Encrypt 获取免费证书

```bash
# 安装 certbot
apt-get install certbot

# 获取证书
certbot certonly --standalone -d your-domain.com

# 证书位置
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem
```

### 修改 nginx/conf.d/default.conf 启用 HTTPS

取消注释 HTTPS 相关配置，修改证书路径：

```nginx
ssl_certificate /etc/nginx/ssl/fullchain.pem;
ssl_certificate_key /etc/nginx/ssl/privkey.pem;
```

挂载证书到容器：

```yaml
nginx:
  volumes:
    - ./nginx/ssl:/etc/nginx/ssl:ro
```

---

## 默认登录账号

```
管理员: admin / admin123
测试用户: testuser / test123
```

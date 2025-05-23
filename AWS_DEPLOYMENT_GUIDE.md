# AWS部署指南 - B站评论检索系统

## 🚀 快速部署方案

### 方案一：EC2 + Docker（推荐）

#### 1. 创建EC2实例
```bash
# 1. 登录AWS控制台，创建EC2实例
# 实例类型：t3.large（推荐）或 t3.medium（最小配置）
# 操作系统：Ubuntu 22.04 LTS
# 存储：至少30GB GP3
# 安全组：开放端口 22(SSH), 80(HTTP), 443(HTTPS)

# 2. 连接到EC2实例
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

#### 2. 初始化EC2实例
```bash
# 运行初始化脚本
curl -fsSL https://raw.githubusercontent.com/your-repo/ec2-setup.sh | bash

# 重新登录以使Docker权限生效
logout
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

#### 3. 部署应用
```bash
# 1. 克隆代码或上传文件
cd /opt/comment-search
# 上传你的项目文件

# 2. 给脚本执行权限
chmod +x deploy.sh

# 3. 运行部署脚本
./deploy.sh
```

#### 4. 访问应用
- 应用地址：`http://your-ec2-public-ip`
- 管理员账户：`admin / admin123`

---

### 方案二：AWS App Runner（最简单）

#### 1. 创建Dockerfile（已创建）
```dockerfile
# 见项目根目录的 Dockerfile
```

#### 2. 推送到ECR
```bash
# 1. 创建ECR仓库
aws ecr create-repository --repository-name comment-search

# 2. 登录ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URI

# 3. 构建和推送镜像
docker build -t comment-search .
docker tag comment-search:latest YOUR_ECR_URI/comment-search:latest
docker push YOUR_ECR_URI/comment-search:latest
```

#### 3. 创建App Runner服务
```bash
# 通过AWS控制台创建App Runner服务
# 选择ECR镜像源
# 配置端口：5001
# 设置环境变量（如需要）
```

---

### 方案三：AWS Elastic Beanstalk

#### 1. 创建应用包
```bash
# 1. 准备部署包
zip -r comment-search-app.zip . -x "*.git*" "node_modules/*" "frontend/node_modules/*"

# 2. 创建 .ebextensions/01_packages.config
mkdir .ebextensions
cat > .ebextensions/01_packages.config << EOF
packages:
  yum:
    docker: []
services:
  sysvinit:
    docker:
      enabled: true
      ensureRunning: true
EOF
```

#### 2. 部署到Elastic Beanstalk
```bash
# 1. 安装EB CLI
pip install awsebcli

# 2. 初始化EB应用
eb init

# 3. 创建环境并部署
eb create comment-search-prod

# 4. 部署更新
eb deploy
```

---

## 🔧 配置说明

### 环境变量
```bash
FLASK_ENV=production
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200
```

### 安全组配置
```
入站规则：
- 端口22 (SSH): 你的IP
- 端口80 (HTTP): 0.0.0.0/0
- 端口443 (HTTPS): 0.0.0.0/0 (如配置SSL)
```

### 实例规格建议
```
最小配置：t3.medium (2vCPU, 4GB RAM)
推荐配置：t3.large (2vCPU, 8GB RAM)
高负载：t3.xlarge (4vCPU, 16GB RAM)
```

---

## 📊 数据导入

### 方法一：通过Web界面
1. 访问管理员面板
2. 点击"数据管理"
3. 上传CSV文件

### 方法二：直接复制到服务器
```bash
# 将数据文件上传到服务器
scp -i your-key.pem -r ./1747748467790_dbexport_209215447 ubuntu@your-ec2-ip:/opt/comment-search/data/
scp -i your-key.pem ./账号大整合3.2xlsx_已提取UID.csv ubuntu@your-ec2-ip:/opt/comment-search/data/

# 重启服务
cd /opt/comment-search
docker-compose restart backend
```

---

## 🛡️ 安全优化

### 1. 配置SSL证书
```bash
# 使用Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 2. 配置防火墙
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
```

### 3. 设置备份
```bash
# 创建每日备份脚本
cat > /opt/comment-search/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec elasticsearch curl -X PUT "localhost:9200/_snapshot/backup" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/usr/share/elasticsearch/snapshots"
  }
}'
EOF

# 添加到crontab
echo "0 2 * * * /opt/comment-search/backup.sh" | crontab -
```

---

## 🔍 监控和维护

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f elasticsearch
```

### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

### 更新应用
```bash
# 1. 备份数据
docker-compose exec elasticsearch curl -X PUT "localhost:9200/_snapshot/backup/snapshot_$(date +%Y%m%d)"

# 2. 拉取新代码
git pull

# 3. 重新构建和部署
docker-compose up -d --build
```

---

## 🎯 估算成本

### EC2方案（月费用）
```
t3.medium: ~$30/月
t3.large: ~$60/月
数据传输: ~$10/月
存储: ~$5/月（30GB）
总计: $45-75/月
```

### App Runner方案（月费用）
```
基础费用: $0.064/vCPU/小时 + $0.007/GB内存/小时
预估: ~$40-80/月（取决于使用量）
```

---

## 🆘 故障排除

### 常见问题
1. **Elasticsearch无法启动**
   ```bash
   # 检查内存是否足够
   free -h
   # 调整ES内存配置
   export ES_JAVA_OPTS="-Xms512m -Xmx512m"
   ```

2. **前端无法访问后端**
   ```bash
   # 检查Nginx配置
   docker-compose logs frontend
   # 检查网络连接
   docker network ls
   ```

3. **数据导入失败**
   ```bash
   # 检查文件权限
   sudo chown -R 1000:1000 /opt/comment-search/data
   ```

---

**总结**：推荐使用 **EC2 + Docker** 方案，部署快速、成本可控、易于维护。 
# AWS部署指南 - B站评论检索系统

## 🚀 快速部署方案（GitHub + EC2 + Docker）

### 前提准备
1. **GitHub仓库**: https://github.com/xinyuana/5.23bili.git
2. **AWS EC2实例**: 已创建并可SSH连接
3. **域名**（可选）: 用于生产环境访问

---

### 🎯 一键部署到AWS EC2

#### 第一步：连接到EC2实例
```bash
# 使用您的SSH密钥连接到EC2
ssh -i "macmiyao.pem" ubuntu@ec2-13-251-31-12.ap-southeast-1.compute.amazonaws.com
```

#### 第二步：下载并运行一键部署脚本
```bash
# 下载部署脚本
curl -fsSL https://raw.githubusercontent.com/xinyuana/5.23bili/main/github-deploy.sh -o github-deploy.sh

# 给脚本执行权限
chmod +x github-deploy.sh

# 运行部署脚本
./github-deploy.sh
```

#### 第三步：输入GitHub仓库地址
当脚本提示时，输入：
```
GitHub仓库地址: https://github.com/xinyuana/5.23bili.git
```

#### 第四步：等待自动部署完成
脚本会自动完成以下操作：
- ✅ 更新系统和安装依赖
- ✅ 安装Docker和Docker Compose
- ✅ 安装Node.js
- ✅ 克隆GitHub代码
- ✅ 构建前端应用
- ✅ 启动所有服务（Elasticsearch + 后端 + 前端）
- ✅ 执行健康检查

#### 第五步：访问应用
部署完成后，访问：
- **应用地址**: `http://ec2-13-251-31-12.ap-southeast-1.compute.amazonaws.com`
- **管理员账户**: `admin / admin123`

---

### 🔄 手动部署方式（可选）

如果自动部署脚本有问题，可以手动执行：

```bash
# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装基础工具
sudo apt install -y git curl jq htop

# 3. 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 4. 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 5. 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 6. 重新登录使Docker权限生效
exit
ssh -i "macmiyao.pem" ubuntu@ec2-13-251-31-12.ap-southeast-1.compute.amazonaws.com

# 7. 克隆代码
sudo mkdir -p /opt/comment-search
sudo chown $USER:$USER /opt/comment-search
cd /opt/comment-search
git clone https://github.com/xinyuana/5.23bili.git .

# 8. 构建前端
cd frontend
npm install
npm run build
cd ..

# 9. 启动服务
docker-compose up -d --build

# 10. 检查服务状态
docker-compose ps
```

---

### 🔄 代码更新流程

#### 方法一：Git Pull更新
```bash
# 连接到服务器
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip
cd /opt/comment-search

# 拉取最新代码
git pull origin main

# 重新构建和部署
./deploy.sh

# 或者分步执行：
# 1. 重新构建前端
cd frontend && npm run build && cd ..

# 2. 重启服务
docker-compose up -d --build
```

#### 方法二：GitHub Actions自动部署（高级）
创建 `.github/workflows/deploy.yml`：
```yaml
name: Deploy to AWS EC2

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to EC2
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.EC2_HOST }}
        username: ubuntu
        key: ${{ secrets.EC2_KEY }}
        script: |
          cd /opt/comment-search
          git pull origin main
          ./deploy.sh
```

---

### 🔧 环境变量配置

创建 `.env` 文件（可选）：
```bash
# 在服务器上创建环境变量文件
cat > .env << EOF
FLASK_ENV=production
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200
# 添加其他必要的环境变量
EOF
```

---

### 🛡️ 安全配置

#### 1. 配置防火墙
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw status
```

#### 2. 配置SSL证书（生产环境推荐）
```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书（需要域名）
sudo certbot --nginx -d your-domain.com

# 配置自动续期
sudo crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

#### 3. 配置域名（可选）
```bash
# 修改nginx配置支持域名
sudo nano /opt/comment-search/nginx.conf
# 将 server_name _; 改为 server_name your-domain.com;

# 重启nginx
docker-compose restart frontend
```

---

### 📊 数据导入

#### 方法一：通过SCP上传数据文件
```bash
# 从本地上传数据文件到服务器
scp -i "your-key.pem" -r ./1747748467790_dbexport_209215447 ubuntu@your-ec2-ip:/opt/comment-search/data/
scp -i "your-key.pem" ./账号大整合3.2xlsx_已提取UID.csv ubuntu@your-ec2-ip:/opt/comment-search/data/

# 重启后端服务以重新加载数据
docker-compose restart backend
```

#### 方法二：通过Web界面上传
1. 访问 `http://your-ec2-ip/admin`
2. 登录管理员账户：`admin / admin123`
3. 进入"数据管理"页面
4. 上传CSV文件

---

### 🔍 监控和维护

#### 查看服务状态
```bash
# 查看所有容器状态
docker-compose ps

# 查看服务日志
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f elasticsearch
docker-compose logs -f frontend

# 查看系统资源使用
htop
df -h
```

#### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
docker-compose restart elasticsearch
```

#### 备份数据
```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p backups

# 备份Elasticsearch数据
docker-compose exec -T elasticsearch curl -X PUT "localhost:9200/_snapshot/backup_$DATE" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/usr/share/elasticsearch/snapshots/backup_'$DATE'"
  }
}'

echo "备份完成: backup_$DATE"
EOF

chmod +x backup.sh

# 设置自动备份（每天凌晨2点）
echo "0 2 * * * /opt/comment-search/backup.sh" | crontab -
```

---

### 💰 成本估算（月费用）

#### EC2实例
- t3.medium: ~$30/月
- t3.large: ~$60/月  
- t3.xlarge: ~$120/月

#### 其他费用
- 数据传输: ~$10/月
- 存储(30GB EBS): ~$3/月
- 弹性IP: ~$3.6/月

#### 总计：$46-136/月

---

### 🆘 故障排除

#### 常见问题

1. **Docker权限问题**
   ```bash
   sudo usermod -aG docker $USER
   # 重新登录
   ```

2. **端口被占用**
   ```bash
   sudo lsof -i :80
   sudo lsof -i :5001
   # 杀死占用进程或修改端口
   ```

3. **Elasticsearch内存不足**
   ```bash
   # 检查可用内存
   free -h
   # 调整ES内存配置
   # 在docker-compose.yml中修改ES_JAVA_OPTS
   ```

4. **前端无法连接后端**
   ```bash
   # 检查网络连接
   docker network ls
   docker-compose logs frontend
   docker-compose logs backend
   ```

5. **Git拉取失败**
   ```bash
   # 检查SSH密钥或使用HTTPS
   git remote set-url origin https://github.com/username/repo.git
   ```

#### 日志查看
```bash
# 查看最近的错误日志
docker-compose logs --tail=100 backend
docker-compose logs --tail=100 elasticsearch

# 实时查看日志
docker-compose logs -f
```

---

## 🎉 完成部署

恭喜！您的B站评论检索系统已成功部署到AWS。

**访问地址**：`http://your-ec2-public-ip`
**管理员登录**：`admin / admin123`

**后续优化建议**：
1. 配置域名和SSL证书
2. 设置监控和告警
3. 配置自动备份
4. 优化性能和安全设置 
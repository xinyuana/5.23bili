# B站评论检索系统 - GitHub一键部署指南

## 🚀 一键部署到AWS EC2

### 前提条件
- **GitHub仓库**: https://github.com/xinyuana/5.23bili.git（已就绪）
- **AWS EC2实例**: 已连接成功
- **SSH密钥**: macmiyao.pem

### ⚡ 超快速部署（推荐）

#### 1. 连接到EC2实例
```bash
ssh -i "macmiyao.pem" ubuntu@ec2-13-251-31-12.ap-southeast-1.compute.amazonaws.com
```

#### 2. 一键部署命令
```bash
# 直接运行一键部署（推荐）
curl -fsSL https://raw.githubusercontent.com/xinyuana/5.23bili/main/github-deploy.sh | bash -s -- https://github.com/xinyuana/5.23bili.git

# 或者分步执行
curl -fsSL https://raw.githubusercontent.com/xinyuana/5.23bili/main/github-deploy.sh -o deploy.sh
chmod +x deploy.sh
./deploy.sh
# 然后输入：https://github.com/xinyuana/5.23bili.git
```

#### 3. 等待部署完成
脚本会自动：
- ✅ 安装所有依赖（Docker、Node.js等）
- ✅ 克隆GitHub代码
- ✅ 构建前端应用
- ✅ 启动所有服务
- ✅ 显示访问地址

#### 4. 访问应用
- **应用地址**: `http://ec2-13-251-31-12.ap-southeast-1.compute.amazonaws.com`
- **管理员账户**: `admin / admin123`

---

## 🔧 常用运维命令

### 查看服务状态
```bash
cd /opt/comment-search
docker-compose ps
docker-compose logs -f
```

### 重启服务
```bash
cd /opt/comment-search
docker-compose restart
```

### 更新代码
```bash
cd /opt/comment-search
./update.sh
```

### 查看系统资源
```bash
htop
df -h
docker stats
```

---

## 📊 数据上传方式

### 方法一：Web界面上传（推荐）
1. 访问 `http://ec2-13-251-31-12.ap-southeast-1.compute.amazonaws.com/admin`
2. 登录：`admin / admin123`
3. 进入"数据管理"页面
4. 上传CSV文件

### 方法二：SCP命令上传
```bash
# 从本地上传数据文件到服务器
scp -i "macmiyao.pem" -r ./data-files ubuntu@ec2-13-251-31-12.ap-southeast-1.compute.amazonaws.com:/opt/comment-search/data/

# 重启后端服务使数据生效
ssh -i "macmiyao.pem" ubuntu@ec2-13-251-31-12.ap-southeast-1.compute.amazonaws.com "cd /opt/comment-search && docker-compose restart backend"
```

---

## 🚀 GitHub Actions自动部署（高级）

如果您想要代码推送自动部署，可以设置GitHub Actions：

### 1. 在GitHub仓库中创建 `.github/workflows/deploy.yml`:
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
        host: ec2-13-251-31-12.ap-southeast-1.compute.amazonaws.com
        username: ubuntu
        key: ${{ secrets.EC2_PRIVATE_KEY }}
        script: |
          cd /opt/comment-search
          git pull origin main
          ./update.sh
```

### 2. 设置GitHub Secrets：
- 进入GitHub仓库设置 → Secrets and variables → Actions
- 添加 `EC2_PRIVATE_KEY`：您的SSH私钥内容

---

## 🛠️ 故障排除

### 常见问题及解决方案

#### 1. 服务无法启动
```bash
# 查看错误日志
cd /opt/comment-search
docker-compose logs backend
docker-compose logs elasticsearch

# 检查端口占用
sudo lsof -i :80
sudo lsof -i :5001
sudo lsof -i :9200
```

#### 2. 内存不足
```bash
# 检查内存使用
free -h

# 重启服务释放内存
docker-compose restart
```

#### 3. 磁盘空间不足
```bash
# 清理Docker镜像和容器
docker system prune -a

# 清理系统日志
sudo journalctl --vacuum-time=3d
```

#### 4. 无法访问应用
```bash
# 检查防火墙设置
sudo ufw status

# 检查AWS安全组
# 确保开放了80端口（HTTP）
```

---

## 📋 部署验证清单

- [ ] EC2实例正常运行
- [ ] SSH可以正常连接
- [ ] 一键部署脚本执行成功
- [ ] 所有Docker容器正常运行
- [ ] 可以访问Web界面
- [ ] 管理员账户可以登录
- [ ] 数据导入功能正常

---

## 💡 部署成功后的下一步

1. **导入数据**: 通过管理后台导入您的B站数据
2. **创建用户**: 为团队成员创建不同权限的用户账号
3. **配置域名**: 将域名指向EC2公网IP（可选）
4. **设置监控**: 配置服务监控和告警
5. **数据备份**: 定期备份重要数据

---

**🎉 恭喜！您的B站评论检索系统已成功部署到AWS！**

如有问题，请查看详细部署指南：`AWS_DEPLOYMENT_GUIDE.md` 
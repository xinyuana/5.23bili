#!/bin/bash

# AWS EC2部署脚本
echo "🚀 开始部署B站评论检索系统到AWS..."

# 1. 构建前端
echo "📦 构建前端应用..."
cd frontend
npm install
npm run build
cd ..

# 2. 创建数据目录
echo "📁 准备数据目录..."
mkdir -p data
cp -r 1747748467790_dbexport_209215447 data/ 2>/dev/null || echo "数据文件不存在，跳过"
cp 账号大整合3.2xlsx_已提取UID.csv data/ 2>/dev/null || echo "账号文件不存在，跳过"

# 3. 构建和启动Docker容器
echo "🐳 启动Docker容器..."
docker-compose down
docker-compose up -d --build

# 4. 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 5. 检查服务状态
echo "🔍 检查服务状态..."
echo "Elasticsearch: $(curl -s http://localhost:9200/_cluster/health | jq -r .status 2>/dev/null || echo '检查失败')"
echo "Backend: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:5001/health || echo '检查失败')"
echo "Frontend: $(curl -s -o /dev/null -w '%{http_code}' http://localhost/health || echo '检查失败')"

echo "✅ 部署完成！"
echo "🌐 访问地址: http://你的EC2公网IP"
echo "👤 管理员账户: admin / admin123" 
#!/bin/bash

# EC2实例初始化脚本 (Ubuntu 22.04)
echo "🔧 初始化EC2实例..."

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
echo "🐳 安装Docker..."
sudo apt install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动Docker服务
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

# 安装Docker Compose
echo "📦 安装Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 安装其他工具
echo "🛠️ 安装其他工具..."
sudo apt install -y git curl jq nodejs npm

# 创建应用目录
sudo mkdir -p /opt/comment-search
sudo chown $USER:$USER /opt/comment-search

echo "✅ EC2实例初始化完成！"
echo "📝 接下来的步骤："
echo "   1. 上传代码到 /opt/comment-search"
echo "   2. 运行 ./deploy.sh" 
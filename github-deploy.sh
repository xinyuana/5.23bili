#!/bin/bash

# GitHub自动部署脚本
# 适用于AWS EC2 Ubuntu 22.04

set -e

echo "🚀 开始GitHub自动部署..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}请不要使用root用户执行此脚本${NC}"
    exit 1
fi

# 函数：打印状态
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. 更新系统
print_status "更新系统..."
sudo apt update && sudo apt upgrade -y

# 2. 安装基础工具
print_status "安装基础工具..."
sudo apt install -y git curl jq htop

# 3. 安装Docker
if ! command -v docker &> /dev/null; then
    print_status "安装Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
else
    print_status "Docker已安装，跳过..."
fi

# 4. 安装Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_status "安装Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    print_status "Docker Compose已安装，跳过..."
fi

# 5. 安装Node.js
if ! command -v node &> /dev/null; then
    print_status "安装Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    print_status "Node.js已安装，跳过..."
fi

# 6. 创建应用目录
print_status "创建应用目录..."
sudo mkdir -p /opt/comment-search
sudo chown $USER:$USER /opt/comment-search

# 7. 获取GitHub仓库地址
echo ""
echo -e "${YELLOW}请输入GitHub仓库地址：${NC}"
echo "例如：https://github.com/username/repo-name.git"
read -p "GitHub仓库地址: " GITHUB_REPO

if [ -z "$GITHUB_REPO" ]; then
    print_error "GitHub仓库地址不能为空"
    exit 1
fi

# 8. 克隆代码
print_status "从GitHub克隆代码..."
cd /opt/comment-search

if [ -d ".git" ]; then
    print_status "检测到已存在的Git仓库，拉取最新代码..."
    git pull origin main
else
    print_status "克隆新的仓库..."
    git clone $GITHUB_REPO .
fi

# 9. 给脚本执行权限
print_status "设置脚本权限..."
chmod +x deploy.sh 2>/dev/null || print_warning "deploy.sh不存在"
chmod +x ec2-setup.sh 2>/dev/null || print_warning "ec2-setup.sh不存在"

# 10. 创建数据目录
mkdir -p data

# 11. 检查Docker组权限
if ! groups $USER | grep -q docker; then
    print_warning "用户不在docker组中，需要重新登录"
    print_status "执行以下命令重新登录："
    echo "logout && ssh -i \"your-key.pem\" ubuntu@your-ec2-ip"
    echo "然后重新运行此脚本"
    exit 0
fi

# 12. 构建前端
if [ -d "frontend" ]; then
    print_status "构建前端应用..."
    cd frontend
    npm install
    npm run build
    cd ..
else
    print_warning "未找到frontend目录"
fi

# 13. 启动服务
print_status "启动Docker服务..."
docker-compose down 2>/dev/null || true
docker-compose up -d --build

# 14. 等待服务启动
print_status "等待服务启动..."
sleep 30

# 15. 检查服务状态
print_status "检查服务状态..."

# 检查容器状态
print_status "Docker容器状态："
docker-compose ps

# 检查服务健康状态
echo ""
print_status "服务健康检查："

ES_STATUS=$(curl -s http://localhost:9200/_cluster/health 2>/dev/null | jq -r .status 2>/dev/null || echo "检查失败")
echo "Elasticsearch: $ES_STATUS"

BACKEND_STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:5001/health 2>/dev/null || echo "检查失败")
echo "Backend: $BACKEND_STATUS"

FRONTEND_STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://localhost/health 2>/dev/null || echo "检查失败")
echo "Frontend: $FRONTEND_STATUS"

# 16. 获取EC2公网IP
print_status "获取访问地址..."
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "无法获取公网IP")

echo ""
echo -e "${GREEN}🎉 部署完成！${NC}"
echo ""
echo -e "${YELLOW}访问信息：${NC}"
echo "应用地址: http://$PUBLIC_IP"
echo "管理员账户: admin"
echo "管理员密码: admin123"
echo ""
echo -e "${YELLOW}常用命令：${NC}"
echo "查看日志: docker-compose logs -f"
echo "重启服务: docker-compose restart"
echo "停止服务: docker-compose down"
echo "更新代码: git pull && docker-compose up -d --build"
echo ""
echo -e "${YELLOW}数据上传：${NC}"
echo "可以通过Web界面上传数据文件，或使用以下命令从本地上传："
echo "scp -i \"your-key.pem\" your-data-file ubuntu@$PUBLIC_IP:/opt/comment-search/data/"

# 17. 创建更新脚本
print_status "创建代码更新脚本..."
cat > update.sh << 'EOF'
#!/bin/bash
echo "🔄 更新代码..."
cd /opt/comment-search

# 拉取最新代码
git pull origin main

# 重新构建前端
if [ -d "frontend" ]; then
    cd frontend
    npm install
    npm run build
    cd ..
fi

# 重启服务
docker-compose up -d --build

echo "✅ 更新完成！"
EOF

chmod +x update.sh

print_status "已创建update.sh脚本，用于快速更新代码"
echo "使用方法: ./update.sh"

echo ""
print_status "部署脚本执行完成！" 
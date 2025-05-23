#!/bin/bash

# B站评论检索系统启动脚本

echo "🚀 启动B站评论检索系统..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装Node.js"
    exit 1
fi

# 检查Elasticsearch是否运行
if ! curl -s http://localhost:9200 > /dev/null; then
    echo "⚠️  Elasticsearch未运行，正在启动..."
    if [ -d "elasticsearch-9.0.1" ]; then
        cd elasticsearch-9.0.1
        ./bin/elasticsearch &
        cd ..
        echo "⏳ 等待Elasticsearch启动..."
        sleep 10
    else
        echo "❌ 未找到Elasticsearch目录，请确保elasticsearch-9.0.1目录存在"
        exit 1
    fi
fi

# 安装Python依赖
echo "📦 安装Python依赖..."
pip3 install -r requirements.txt

# 启动后端服务
echo "🔧 启动后端服务..."
python3 app.py &
BACKEND_PID=$!

# 等待后端启动
sleep 5

# 安装前端依赖并启动
echo "🎨 启动前端服务..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!

cd ..

echo "✅ 系统启动完成！"
echo ""
echo "🌐 前端地址: http://localhost:3000"
echo "🔧 后端API: http://localhost:5000"
echo "🔍 Elasticsearch: http://localhost:9200"
echo ""
echo "👤 默认账号:"
echo "   管理员: admin / admin123"
echo "   普通用户: user1 / user123"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
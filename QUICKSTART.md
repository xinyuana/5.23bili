# 快速启动指南

## 🚀 一键启动

### 方法一：使用启动脚本（推荐）

```bash
# 给脚本执行权限
chmod +x start.sh

# 启动系统
./start.sh
```

### 方法二：手动启动

#### 1. 启动Elasticsearch
```bash
cd elasticsearch-9.0.1
./bin/elasticsearch
```

#### 2. 启动后端
```bash
# 安装依赖
pip install -r requirements.txt

# 启动Flask应用
python app.py
```

#### 3. 启动前端
```bash
cd frontend
npm install
npm run dev
```

## 📊 导入数据

### 自动导入
```bash
python import_data.py
```

### 手动导入
1. 登录管理后台：http://localhost:3000
2. 使用管理员账号：admin / admin123
3. 进入"管理后台" -> "数据管理"
4. 点击"导入数据"

## 🧪 测试系统

```bash
python test_system.py
```

## 🌐 访问地址

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:5000
- **Elasticsearch**: http://localhost:9200

## 👤 默认账号

- **管理员**: admin / admin123
- **普通用户**: user1 / user123

## 📁 数据文件

确保以下文件存在：
- `1747748467790_dbexport_209215447/2025-05-20-21-41-08_EXPORT_CSV_19274722_345_bilibili_video_0.csv`
- `1747748467790_dbexport_209215447/2025-05-20-21-41-11_EXPORT_CSV_19274722_637_bilibili_video_comment_1.csv`
- `账号大整合3.2xlsx_已提取UID.csv`

## 🔧 常见问题

### Q: Elasticsearch启动失败
```bash
# 检查Java版本
java -version

# 检查端口占用
lsof -i :9200

# 查看Elasticsearch日志
tail -f elasticsearch-9.0.1/logs/elasticsearch.log
```

### Q: 前端无法访问后端
检查CORS设置和代理配置：
```javascript
// frontend/vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

### Q: 数据导入失败
1. 确认CSV文件路径正确
2. 检查Elasticsearch连接
3. 查看控制台错误信息

## 🐳 Docker部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 📝 使用说明

### 搜索功能
1. 选择搜索类型（视频/评论）
2. 输入关键词
3. 设置筛选条件
4. 点击搜索按钮

### 高级功能
- **项目筛选**: 按项目隔离数据
- **时间范围**: 精确到分钟的时间筛选
- **排序选项**: 多种排序方式
- **相似评论**: 基于内容相似度查找
- **结果高亮**: 关键词高亮显示

### 管理功能（仅管理员）
- **用户管理**: 创建、编辑、删除用户
- **权限控制**: 设置用户项目访问权限
- **数据导入**: 批量导入CSV数据

## 🔄 更新数据

### 增量更新
```bash
# 导入新数据（自动去重）
python import_data.py
```

### 重建索引
```bash
# 删除现有索引
curl -X DELETE "localhost:9200/videos_search"
curl -X DELETE "localhost:9200/comments_search"

# 重新导入数据
python import_data.py
```

## 📈 性能优化

### Elasticsearch优化
```bash
# 增加JVM内存
export ES_JAVA_OPTS="-Xms1g -Xmx1g"

# 调整刷新间隔
curl -X PUT "localhost:9200/videos_search/_settings" -H 'Content-Type: application/json' -d'
{
  "refresh_interval": "30s"
}
'
```

### 前端优化
```bash
# 生产构建
cd frontend
npm run build

# 使用Nginx提供静态文件
nginx -c /path/to/nginx.conf
```

## 🛠️ 开发模式

### 热重载开发
```bash
# 后端热重载
export FLASK_ENV=development
python app.py

# 前端热重载
cd frontend
npm run dev
```

### 调试模式
```bash
# 启用详细日志
export FLASK_DEBUG=true
python app.py
```

## 📞 获取帮助

如果遇到问题：
1. 查看日志文件
2. 运行测试脚本
3. 检查网络连接
4. 确认服务状态

更多详细信息请参考 [README.md](README.md) 
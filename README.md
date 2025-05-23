# B站评论检索系统

基于Elasticsearch的B站视频和评论检索系统，支持多维度搜索、筛选和相似评论查找。

## 功能特性

### 核心功能
- 🔍 **全文检索**: 支持视频标题、描述、评论内容的全文搜索
- 🎯 **精确筛选**: 按UP主、时间范围、项目等多维度筛选
- 🔗 **链接检索**: 支持通过视频链接直接查找
- 📊 **排序功能**: 按时间、播放量、点赞数等排序
- 🎨 **高亮显示**: 搜索结果关键词高亮
- 🔄 **相似评论**: 基于内容相似度查找相关评论
- 📄 **分页浏览**: 支持大量数据的分页展示

### 用户管理
- 👤 **角色权限**: 管理员和普通用户角色
- 🔐 **JWT认证**: 安全的用户认证机制
- 🏢 **项目权限**: 基于项目的数据访问控制
- ⚙️ **用户管理**: 管理员可管理用户账号

### 数据管理
- 📥 **数据导入**: 支持CSV格式的批量数据导入
- 🔄 **增量更新**: 支持数据的增量更新和去重
- 📈 **项目管理**: 多项目数据隔离和管理

## 技术栈

### 后端
- **Flask**: Python Web框架
- **Elasticsearch**: 搜索引擎和数据存储
- **Pandas**: 数据处理和清洗
- **JWT**: 用户认证
- **Jieba**: 中文分词

### 前端
- **Vue 3**: 前端框架
- **Element Plus**: UI组件库
- **Pinia**: 状态管理
- **Vue Router**: 路由管理
- **Axios**: HTTP客户端
- **Vite**: 构建工具

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- Elasticsearch 8.x
- Redis (可选，用于任务队列)

### 1. 启动Elasticsearch

```bash
# 进入Elasticsearch目录
cd elasticsearch-9.0.1

# 启动Elasticsearch
./bin/elasticsearch
```

### 2. 后端设置

```bash
# 安装Python依赖
pip install -r requirements.txt

# 配置环境变量
cp config.env .env
# 编辑.env文件，配置Elasticsearch连接信息

# 启动Flask应用
python app.py
```

### 3. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用

- 前端地址: http://localhost:3000
- 后端API: http://localhost:5000

### 5. 默认账号

- **管理员**: admin / admin123
- **普通用户**: user1 / user123

## 数据导入

### 1. 准备数据文件

确保以下CSV文件存在：
- `1747748467790_dbexport_209215447/2025-05-20-21-41-08_EXPORT_CSV_19274722_345_bilibili_video_0.csv` (视频数据)
- `1747748467790_dbexport_209215447/2025-05-20-21-41-11_EXPORT_CSV_19274722_637_bilibili_video_comment_1.csv` (评论数据)
- `账号大整合3.2xlsx_已提取UID.csv` (账号数据)

### 2. 导入数据

通过管理后台的数据管理页面，或者直接调用API：

```bash
curl -X POST http://localhost:5000/admin/data/import \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data_type": "all", "project_id": "巨书"}'
```

## API文档

### 认证接口
- `POST /auth/login` - 用户登录
- `GET /auth/me` - 获取当前用户信息

### 搜索接口
- `POST /search/videos` - 搜索视频
- `POST /search/comments` - 搜索评论
- `GET /comments/{id}/similar` - 查找相似评论

### 管理接口
- `GET /admin/users` - 获取用户列表
- `POST /admin/users` - 创建用户
- `PUT /admin/users/{id}` - 更新用户
- `DELETE /admin/users/{id}` - 删除用户
- `POST /admin/data/import` - 导入数据

### 项目接口
- `GET /projects` - 获取项目列表

## 搜索功能说明

### 视频搜索
- **关键词搜索**: 在标题、描述、UP主昵称中搜索
- **视频标题**: 精确匹配视频标题
- **UP主信息**: 按UP主昵称或UID搜索
- **视频链接**: 通过B站链接查找视频
- **时间筛选**: 按视频发布时间范围筛选
- **排序选项**: 按发布时间或播放量排序

### 评论搜索
- **内容搜索**: 在评论内容中搜索关键词
- **评论者信息**: 按评论者昵称或UID搜索
- **视频关联**: 查找特定视频的评论
- **时间筛选**: 按评论发布时间范围筛选
- **相似评论**: 基于内容相似度查找相关评论

### 高级功能
- **项目隔离**: 不同项目的数据相互隔离
- **权限控制**: 用户只能访问授权的项目数据
- **结果高亮**: 搜索关键词在结果中高亮显示
- **分页浏览**: 大量结果支持分页查看

## 部署说明

### Docker部署 (推荐)

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

### 生产环境部署

1. **后端部署**:
   ```bash
   # 使用Gunicorn启动
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **前端部署**:
   ```bash
   # 构建生产版本
   npm run build
   
   # 使用Nginx提供静态文件服务
   ```

3. **Nginx配置**:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           root /path/to/frontend/dist;
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 开发说明

### 项目结构
```
├── app.py                 # Flask主应用
├── services/              # 业务逻辑层
│   ├── elasticsearch_service.py
│   ├── auth_service.py
│   └── data_service.py
├── frontend/              # Vue前端
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 通用组件
│   │   ├── stores/        # 状态管理
│   │   └── utils/         # 工具函数
├── data/                  # 数据文件
├── requirements.txt       # Python依赖
└── README.md             # 项目说明
```

### 开发规范
- 后端使用Flask Blueprint组织路由
- 前端使用Vue 3 Composition API
- 统一的错误处理和日志记录
- RESTful API设计
- 响应式UI设计

## 常见问题

### Q: Elasticsearch连接失败
A: 检查Elasticsearch是否正常启动，端口是否正确配置

### Q: 数据导入失败
A: 确认CSV文件格式正确，检查文件路径和权限

### Q: 搜索结果为空
A: 确认数据已正确导入，检查用户权限和项目配置

### Q: 前端无法访问后端API
A: 检查CORS配置和代理设置

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 联系方式

如有问题，请通过以下方式联系：
- 邮箱: your-email@example.com
- GitHub: https://github.com/your-username/comment-search-system 
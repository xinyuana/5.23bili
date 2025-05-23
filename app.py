from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import jwt
import os
from functools import wraps
from dotenv import load_dotenv

# 导入各个模块
from services.elasticsearch_service import ElasticsearchService
from services.auth_service import AuthService
from services.data_service import DataService

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# 启用CORS
CORS(app)

# 初始化服务
es_service = ElasticsearchService()
auth_service = AuthService()
data_service = DataService()

# JWT认证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': '缺少认证令牌'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = auth_service.get_user_by_id(data['user_id'])
            if not current_user:
                return jsonify({'message': '用户不存在'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': '令牌已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '无效令牌'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# 管理员权限装饰器
def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.get('role') != 'admin':
            return jsonify({'message': '需要管理员权限'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

# 认证路由
@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'message': '用户名和密码不能为空'}), 400
        
        user = auth_service.authenticate_user(username, password)
        if not user:
            return jsonify({'message': '用户名或密码错误'}), 401
        
        # 生成JWT令牌
        token = jwt.encode({
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'project_access': user.get('project_access', [])
            }
        })
    except Exception as e:
        return jsonify({'message': f'登录失败: {str(e)}'}), 500

@app.route('/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    return jsonify({
        'user': {
            'id': current_user['id'],
            'username': current_user['username'],
            'role': current_user['role'],
            'project_access': current_user.get('project_access', [])
        }
    })

# 搜索路由
@app.route('/search/videos', methods=['POST'])
@token_required
def search_videos(current_user):
    try:
        data = request.get_json()
        
        # 检查项目权限
        project_id = data.get('project_id')
        if current_user['role'] != 'admin' and project_id:
            if project_id not in current_user.get('project_access', []):
                return jsonify({'message': '无权访问该项目'}), 403
        
        results = es_service.search_videos(data, current_user)
        return jsonify(results)
    except Exception as e:
        return jsonify({'message': f'搜索失败: {str(e)}'}), 500

@app.route('/search/comments', methods=['POST'])
@token_required
def search_comments(current_user):
    try:
        data = request.get_json()
        
        # 检查项目权限
        project_id = data.get('project_id')
        if current_user['role'] != 'admin' and project_id:
            if project_id not in current_user.get('project_access', []):
                return jsonify({'message': '无权访问该项目'}), 403
        
        results = es_service.search_comments(data, current_user)
        return jsonify(results)
    except Exception as e:
        return jsonify({'message': f'搜索失败: {str(e)}'}), 500

@app.route('/comments/<comment_id>/similar', methods=['GET'])
@token_required
def find_similar_comments(current_user, comment_id):
    try:
        results = es_service.find_similar_comments(comment_id, current_user)
        return jsonify(results)
    except Exception as e:
        return jsonify({'message': f'查找相似评论失败: {str(e)}'}), 500

# 管理员路由
@app.route('/admin/users', methods=['GET'])
@token_required
@admin_required
def get_users(current_user):
    try:
        users = auth_service.get_all_users()
        return jsonify({'users': users})
    except Exception as e:
        return jsonify({'message': f'获取用户列表失败: {str(e)}'}), 500

@app.route('/admin/users', methods=['POST'])
@token_required
@admin_required
def create_user(current_user):
    try:
        data = request.get_json()
        user = auth_service.create_user(data)
        return jsonify({'user': user}), 201
    except Exception as e:
        return jsonify({'message': f'创建用户失败: {str(e)}'}), 500

@app.route('/admin/users/<int:user_id>', methods=['PUT'])
@token_required
@admin_required
def update_user(current_user, user_id):
    try:
        data = request.get_json()
        user = auth_service.update_user(user_id, data)
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        return jsonify({'user': user})
    except Exception as e:
        return jsonify({'message': f'更新用户失败: {str(e)}'}), 500

@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(current_user, user_id):
    try:
        success = auth_service.delete_user(user_id)
        if not success:
            return jsonify({'message': '用户不存在'}), 404
        return jsonify({'message': '用户删除成功'})
    except Exception as e:
        return jsonify({'message': f'删除用户失败: {str(e)}'}), 500

@app.route('/admin/data/import', methods=['POST'])
@token_required
@admin_required
def import_data(current_user):
    try:
        data = request.get_json()
        task_id = data_service.import_data_async(data)
        return jsonify({'task_id': task_id, 'message': '数据导入任务已启动'})
    except Exception as e:
        return jsonify({'message': f'启动数据导入失败: {str(e)}'}), 500

@app.route('/admin/data/clear', methods=['POST'])
@token_required
@admin_required
def clear_data(current_user):
    """清空数据"""
    try:
        data = request.get_json()
        data_type = data.get('data_type', 'all')  # 'videos', 'comments', 'all'
        
        success = data_service.clear_data(data_type)
        if success:
            return jsonify({'message': f'数据清空成功'})
        else:
            return jsonify({'message': '数据清空失败'}), 500
    except Exception as e:
        return jsonify({'message': f'清空数据失败: {str(e)}'}), 500

@app.route('/admin/data/statistics', methods=['GET'])
@token_required
@admin_required
def get_data_statistics(current_user):
    """获取数据统计信息"""
    try:
        stats = data_service.get_data_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'message': f'获取统计信息失败: {str(e)}'}), 500

@app.route('/admin/data/upload', methods=['POST'])
@token_required
@admin_required
def upload_data_file(current_user):
    """上传数据文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'message': '没有选择文件'}), 400
        
        file = request.files['file']
        file_type = request.form.get('file_type')  # 'account', 'video', 'comment'
        
        if file.filename == '':
            return jsonify({'message': '没有选择文件'}), 400
        
        # 保存文件并处理
        result = data_service.handle_uploaded_file(file, file_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'message': f'文件上传失败: {str(e)}'}), 500

@app.route('/projects', methods=['GET'])
@token_required
def get_projects(current_user):
    try:
        projects = es_service.get_available_projects(current_user)
        return jsonify({'projects': projects})
    except Exception as e:
        return jsonify({'message': f'获取项目列表失败: {str(e)}'}), 500

@app.route('/time-range', methods=['GET'])
@token_required
def get_time_range(current_user):
    """获取数据的时间范围"""
    try:
        # 获取评论时间范围
        comment_range = es_service.get_time_range('comments')
        video_range = es_service.get_time_range('videos')
        
        return jsonify({
            'time_range': {
                'comment_range': comment_range,
                'video_range': video_range
            },
            'success': True
        })
    except Exception as e:
        return jsonify({'message': f'获取时间范围失败: {str(e)}'}), 500

@app.route('/admin/data/visualization', methods=['POST'])
@token_required
@admin_required
def get_visualization_data(current_user):
    """获取数据可视化统计信息"""
    try:
        data = request.get_json()
        stats = data_service.get_visualization_statistics(data)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'message': f'获取可视化数据失败: {str(e)}'}), 500

# 健康检查
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 
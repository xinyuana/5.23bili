import hashlib
import json
import os
from datetime import datetime

class AuthService:
    def __init__(self):
        self.users_file = 'data/users.json'
        self.ensure_data_dir()
        self.init_default_users()
    
    def ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs('data', exist_ok=True)
    
    def init_default_users(self):
        """初始化默认用户"""
        if not os.path.exists(self.users_file):
            default_users = [
                {
                    'id': 1,
                    'username': 'admin',
                    'password_hash': self.hash_password('admin123'),
                    'role': 'admin',
                    'project_access': [],  # 管理员可以访问所有项目
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': 2,
                    'username': 'user1',
                    'password_hash': self.hash_password('user123'),
                    'role': 'user',
                    'project_access': ['巨书', '康江文'],  # 普通用户只能访问指定项目
                    'created_at': datetime.now().isoformat()
                }
            ]
            self.save_users(default_users)
    
    def hash_password(self, password):
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_users(self):
        """加载用户数据"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_users(self, users):
        """保存用户数据"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    def authenticate_user(self, username, password):
        """用户认证"""
        users = self.load_users()
        password_hash = self.hash_password(password)
        
        for user in users:
            if user['username'] == username and user['password_hash'] == password_hash:
                return user
        return None
    
    def get_user_by_id(self, user_id):
        """根据ID获取用户"""
        users = self.load_users()
        for user in users:
            if user['id'] == user_id:
                return user
        return None
    
    def get_all_users(self):
        """获取所有用户（不包含密码）"""
        users = self.load_users()
        safe_users = []
        for user in users:
            safe_user = user.copy()
            safe_user.pop('password_hash', None)
            safe_users.append(safe_user)
        return safe_users
    
    def create_user(self, user_data):
        """创建新用户"""
        users = self.load_users()
        
        # 检查用户名是否已存在
        for user in users:
            if user['username'] == user_data['username']:
                raise ValueError('用户名已存在')
        
        # 生成新的用户ID
        max_id = max([user['id'] for user in users]) if users else 0
        new_user = {
            'id': max_id + 1,
            'username': user_data['username'],
            'password_hash': self.hash_password(user_data['password']),
            'role': user_data.get('role', 'user'),
            'project_access': user_data.get('project_access', []),
            'created_at': datetime.now().isoformat()
        }
        
        users.append(new_user)
        self.save_users(users)
        
        # 返回安全的用户信息（不包含密码）
        safe_user = new_user.copy()
        safe_user.pop('password_hash')
        return safe_user
    
    def update_user(self, user_id, user_data):
        """更新用户信息"""
        users = self.load_users()
        
        for i, user in enumerate(users):
            if user['id'] == user_id:
                # 更新用户信息
                if 'username' in user_data:
                    # 检查用户名是否与其他用户冲突
                    for other_user in users:
                        if other_user['id'] != user_id and other_user['username'] == user_data['username']:
                            raise ValueError('用户名已存在')
                    user['username'] = user_data['username']
                
                if 'password' in user_data:
                    user['password_hash'] = self.hash_password(user_data['password'])
                
                if 'role' in user_data:
                    user['role'] = user_data['role']
                
                if 'project_access' in user_data:
                    user['project_access'] = user_data['project_access']
                
                user['updated_at'] = datetime.now().isoformat()
                users[i] = user
                self.save_users(users)
                
                # 返回安全的用户信息
                safe_user = user.copy()
                safe_user.pop('password_hash')
                return safe_user
        
        return None
    
    def delete_user(self, user_id):
        """删除用户"""
        users = self.load_users()
        
        for i, user in enumerate(users):
            if user['id'] == user_id:
                if user['role'] == 'admin':
                    # 检查是否是最后一个管理员
                    admin_count = sum(1 for u in users if u['role'] == 'admin')
                    if admin_count <= 1:
                        raise ValueError('不能删除最后一个管理员')
                
                users.pop(i)
                self.save_users(users)
                return True
        
        return False 
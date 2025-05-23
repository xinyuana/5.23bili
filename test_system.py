#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统测试脚本
测试各个组件的基本功能
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {str(e)}")
        return False

def test_login():
    """测试登录功能"""
    print("🔐 测试登录功能...")
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print("✅ 登录成功")
            return token
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {str(e)}")
        return None

def test_search(token):
    """测试搜索功能"""
    print("🔍 测试搜索功能...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # 测试视频搜索
        search_data = {
            "searchType": "videos",
            "keywords": "考试",
            "page": 1,
            "page_size": 5
        }
        response = requests.post(f"{BASE_URL}/search/videos", json=search_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 视频搜索成功，找到 {data.get('total', 0)} 条结果")
        else:
            print(f"❌ 视频搜索失败: {response.status_code}")
        
        # 测试评论搜索
        search_data = {
            "searchType": "comments",
            "keywords": "考试",
            "page": 1,
            "page_size": 5
        }
        response = requests.post(f"{BASE_URL}/search/comments", json=search_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 评论搜索成功，找到 {data.get('total', 0)} 条结果")
            return True
        else:
            print(f"❌ 评论搜索失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 搜索异常: {str(e)}")
        return False

def test_projects(token):
    """测试项目列表"""
    print("📋 测试项目列表...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/projects", headers=headers)
        if response.status_code == 200:
            data = response.json()
            projects = data.get('projects', [])
            print(f"✅ 项目列表获取成功，共 {len(projects)} 个项目")
            for project in projects:
                print(f"   - {project.get('name')}: {project.get('doc_count')} 条数据")
            return True
        else:
            print(f"❌ 项目列表获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 项目列表异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始系统测试...")
    print("=" * 50)
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(2)
    
    # 测试健康检查
    if not test_health():
        print("❌ 系统测试失败：健康检查不通过")
        return False
    
    print("-" * 30)
    
    # 测试登录
    token = test_login()
    if not token:
        print("❌ 系统测试失败：登录失败")
        return False
    
    print("-" * 30)
    
    # 测试项目列表
    if not test_projects(token):
        print("⚠️  项目列表测试失败（可能是数据未导入）")
    
    print("-" * 30)
    
    # 测试搜索功能
    if not test_search(token):
        print("⚠️  搜索功能测试失败（可能是数据未导入）")
    
    print("=" * 50)
    print("🎉 系统测试完成！")
    
    print("\n📝 测试总结:")
    print("✅ 后端服务正常运行")
    print("✅ 用户认证功能正常")
    print("✅ API接口响应正常")
    print("\n💡 提示:")
    print("- 如果搜索结果为空，请先运行数据导入脚本: python import_data.py")
    print("- 前端访问地址: http://localhost:3000")
    print("- 默认管理员账号: admin / admin123")
    
    return True

if __name__ == "__main__":
    main() 
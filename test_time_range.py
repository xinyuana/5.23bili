#!/usr/bin/env python3
"""
时间范围查询测试脚本
"""

import requests
import json
import time
from datetime import datetime

# 测试不同的时间范围
def test_time_range_search():
    base_url = "http://localhost:5001"
    
    # 使用管理员权限
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6ImFkbWluIiwiZXhwIjoyMDAwMDAwMDAwfQ.Hf3_K7w5oWsz1GNdZyOVGwU8P2E6fgUxnH4vB3t8J2c'
    }
    
    # 测试1: 无时间范围的基础搜索
    print("🔍 测试1: 无时间范围的基础搜索")
    payload1 = {
        "page": 1,
        "page_size": 5,
        "keywords": "公务员"
    }
    
    try:
        response = requests.post(f"{base_url}/search/comments", 
                               headers=headers, json=payload1, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 找到 {data.get('total', 0)} 条结果")
            for i, result in enumerate(data.get('results', [])[:3]):
                timestamp = result.get('create_time', 0)
                readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
                print(f"   {i+1}. 时间: {readable_time} (时间戳: {timestamp})")
        else:
            print(f"❌ 请求失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试2: 带时间范围的搜索
    print("🔍 测试2: 带时间范围的搜索")
    
    # 使用2025年5月14日 - 2025年5月15日的时间范围
    start_time = int(datetime(2025, 5, 14).timestamp())
    end_time = int(datetime(2025, 5, 16).timestamp())
    
    print(f"时间范围: {start_time} - {end_time}")
    print(f"可读时间: {datetime.fromtimestamp(start_time)} - {datetime.fromtimestamp(end_time)}")
    
    payload2 = {
        "page": 1,
        "page_size": 5,
        "keywords": "公务员",
        "time_range": {
            "start": start_time,
            "end": end_time
        }
    }
    
    try:
        response = requests.post(f"{base_url}/search/comments", 
                               headers=headers, json=payload2, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 时间范围内找到 {data.get('total', 0)} 条结果")
            for i, result in enumerate(data.get('results', [])[:3]):
                timestamp = result.get('create_time', 0)
                readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
                print(f"   {i+1}. 时间: {readable_time} (时间戳: {timestamp})")
        else:
            print(f"❌ 请求失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_time_range_search() 
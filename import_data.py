#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据导入脚本
用于将CSV数据导入到Elasticsearch中
"""

import os
import sys
from services.data_service import DataService
from services.elasticsearch_service import ElasticsearchService

def main():
    print("🚀 开始导入数据...")
    
    # 初始化服务
    es_service = ElasticsearchService()
    data_service = DataService()
    
    try:
        # 检查Elasticsearch连接
        es_client = es_service.get_es_client()
        if not es_client.info():
            print("❌ 无法连接到Elasticsearch，请确保Elasticsearch正在运行")
            return False
        
        print("✅ Elasticsearch连接成功")
        
        # 创建索引
        print("📋 创建Elasticsearch索引...")
        es_service.create_indices()
        print("✅ 索引创建完成")
        
        # 导入数据 - 移除固定项目ID，让系统自动根据用户ID分配
        import_params = {
            'data_type': 'all'  # 导入所有数据
        }
        
        print("📥 开始导入数据...")
        data_service.import_data_sync(import_params)
        print("✅ 数据导入完成")
        
        # 检查导入结果
        print("📊 检查导入结果...")
        
        # 检查视频数据
        try:
            video_count = es_client.count(index=es_service.video_index)['count']
            print(f"📹 视频数据: {video_count} 条")
        except:
            print("📹 视频数据: 0 条 (索引可能不存在)")
        
        # 检查评论数据
        try:
            comment_count = es_client.count(index=es_service.comment_index)['count']
            print(f"💬 评论数据: {comment_count} 条")
        except:
            print("💬 评论数据: 0 条 (索引可能不存在)")
        
        # 检查项目分布
        try:
            print("\n📊 项目分布统计:")
            project_stats = es_client.search(
                index=es_service.video_index,
                body={
                    "size": 0,
                    "aggs": {
                        "projects": {
                            "terms": {
                                "field": "project_id.keyword",
                                "size": 50
                            }
                        }
                    }
                }
            )
            
            for bucket in project_stats['aggregations']['projects']['buckets']:
                project = bucket['key']
                count = bucket['doc_count']
                print(f"   📹 {project}: {count} 个视频")
                
        except Exception as e:
            print(f"⚠️ 项目统计失败: {str(e)}")
        
        print("🎉 数据导入成功完成！")
        return True
        
    except Exception as e:
        print(f"❌ 数据导入失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
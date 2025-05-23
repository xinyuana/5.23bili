import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import uuid
from services.elasticsearch_service import ElasticsearchService

class DataService:
    def __init__(self):
        self.es_service = ElasticsearchService()
        self.user_project_mapping = None
        
    def load_user_project_mapping(self):
        """加载用户ID到项目的映射关系"""
        if self.user_project_mapping is not None:
            return self.user_project_mapping
            
        account_file = '账号大整合3.2xlsx_已提取UID.csv'
        self.user_project_mapping = {}
        
        if os.path.exists(account_file):
            try:
                df = pd.read_csv(account_file, low_memory=False)
                
                # 建立用户ID到项目的映射
                for _, row in df.iterrows():
                    user_id = str(row.get('用户ID', '')).strip()
                    project = str(row.get('工作表', '')).strip()
                    
                    if user_id and project and user_id != 'nan' and project != 'nan':
                        self.user_project_mapping[user_id] = project
                
                print(f"✅ 成功加载 {len(self.user_project_mapping)} 个用户的项目映射")
                
                # 打印项目统计
                project_counts = {}
                for project in self.user_project_mapping.values():
                    project_counts[project] = project_counts.get(project, 0) + 1
                
                print("📊 项目分布:")
                for project, count in sorted(project_counts.items()):
                    print(f"   {project}: {count} 个用户")
                    
            except Exception as e:
                print(f"⚠️ 加载用户项目映射失败: {str(e)}")
                
        return self.user_project_mapping
    
    def get_user_project(self, user_id):
        """根据用户ID获取项目名称"""
        if self.user_project_mapping is None:
            self.load_user_project_mapping()
            
        return self.user_project_mapping.get(str(user_id), '未分类项目')
        
    def import_data_async(self, import_params):
        """异步导入数据（返回任务ID）"""
        task_id = str(uuid.uuid4())
        
        # 在实际生产环境中，这里应该使用Celery等任务队列
        # 现在我们直接调用同步方法进行演示
        try:
            self.import_data_sync(import_params)
            return task_id
        except Exception as e:
            print(f"数据导入失败: {str(e)}")
            raise
    
    def import_data_sync(self, import_params):
        """同步导入数据"""
        data_type = import_params.get('data_type', 'all')  # 'videos', 'comments', 'all'
        
        # 加载用户项目映射
        self.load_user_project_mapping()
        
        # 确保索引存在
        self.es_service.create_indices()
        
        if data_type in ['videos', 'all']:
            self.import_videos()
        
        if data_type in ['comments', 'all']:
            self.import_comments()
    
    def import_videos(self):
        """导入视频数据"""
        video_files = [
            '1747748467790_dbexport_209215447/2025-05-20-21-41-08_EXPORT_CSV_19274722_345_bilibili_video_0.csv'
        ]
        
        for video_file in video_files:
            if os.path.exists(video_file):
                print(f"正在导入视频文件: {video_file}")
                
                # 分块读取大文件
                chunk_size = 1000
                for chunk in pd.read_csv(video_file, chunksize=chunk_size, low_memory=False):
                    self.process_video_chunk(chunk)
    
    def process_video_chunk(self, df):
        """处理视频数据块"""
        bulk_data = []
        
        for _, row in df.iterrows():
            # 根据用户ID获取项目
            user_id = str(row.get('user_id', ''))
            project_id = self.get_user_project(user_id)
            
            # 清理和转换数据
            doc = {
                'id': str(row.get('id', '')),
                'user_id': user_id,
                'nickname': str(row.get('nickname', '')),
                'avatar': str(row.get('avatar', '')),
                'add_ts': self.convert_timestamp(row.get('add_ts')),
                'last_modify_ts': self.convert_timestamp(row.get('last_modify_ts')),
                'video_id': str(row.get('video_id', '')),
                'video_type': str(row.get('video_type', 'video')),
                'title': str(row.get('title', '')),
                'desc': str(row.get('desc', '')),
                'create_time': self.convert_timestamp(row.get('create_time')),
                'liked_count': self.safe_int(row.get('liked_count', 0)),
                'video_play_count': self.safe_int(row.get('video_play_count', 0)),
                'video_danmaku': self.safe_int(row.get('video_danmaku', 0)),
                'video_comment': self.safe_int(row.get('video_comment', 0)),
                'video_url': str(row.get('video_url', '')),
                'video_cover_url': str(row.get('video_cover_url', '')),
                'source_keyword': str(row.get('source_keyword', '')),
                'project_id': project_id
            }
            
            # 构建批量插入数据
            bulk_data.append({
                '_index': self.es_service.video_index,
                '_id': doc['video_id'],  # 使用video_id作为文档ID实现去重
                '_source': doc
            })
        
        # 批量插入Elasticsearch
        if bulk_data:
            self.bulk_insert(bulk_data)
    
    def import_comments(self):
        """导入评论数据"""
        comment_files = [
            '1747748467790_dbexport_209215447/2025-05-20-21-41-11_EXPORT_CSV_19274722_637_bilibili_video_comment_1.csv'
        ]
        
        # 首先构建视频ID到项目的映射
        self.build_video_project_mapping()
        
        for comment_file in comment_files:
            if os.path.exists(comment_file):
                print(f"正在导入评论文件: {comment_file}")
                
                # 分块读取大文件
                chunk_size = 1000
                for chunk in pd.read_csv(comment_file, chunksize=chunk_size, low_memory=False):
                    self.process_comment_chunk(chunk)
    
    def build_video_project_mapping(self):
        """构建视频ID到项目的映射关系，同时构建视频详细信息映射"""
        if hasattr(self, 'video_project_mapping'):
            return
            
        self.video_project_mapping = {}
        self.video_info_mapping = {}  # 添加视频详细信息映射
        video_files = [
            '1747748467790_dbexport_209215447/2025-05-20-21-41-08_EXPORT_CSV_19274722_345_bilibili_video_0.csv'
        ]
        
        print("🔗 构建视频-项目映射关系...")
        
        for video_file in video_files:
            if os.path.exists(video_file):
                # 分块读取视频文件
                chunk_size = 5000
                for chunk in pd.read_csv(video_file, chunksize=chunk_size, low_memory=False):
                    for _, row in chunk.iterrows():
                        video_id = str(row.get('video_id', ''))
                        user_id = str(row.get('user_id', ''))
                        project_id = self.get_user_project(user_id)
                        
                        if video_id and video_id != 'nan':
                            self.video_project_mapping[video_id] = project_id
                            # 同时保存视频详细信息
                            self.video_info_mapping[video_id] = {
                                'video_title': str(row.get('title', '')),
                                'video_url': str(row.get('video_url', '')),
                                'video_uploader_nickname': str(row.get('nickname', '')),
                                'video_uploader_uid': str(row.get('user_id', ''))
                            }
        
        print(f"✅ 构建了 {len(self.video_project_mapping)} 个视频的项目映射")
        print(f"✅ 构建了 {len(self.video_info_mapping)} 个视频的详细信息映射")
    
    def get_video_project(self, video_id):
        """根据视频ID获取项目名称"""
        if hasattr(self, 'video_project_mapping'):
            return self.video_project_mapping.get(str(video_id), '未分类项目')
        else:
            return '未分类项目'

    def process_comment_chunk(self, df):
        """处理评论数据块"""
        bulk_data = []
        
        for _, row in df.iterrows():
            # 根据视频ID获取项目（而不是评论者的user_id）
            video_id = str(row.get('video_id', ''))
            project_id = self.get_video_project(video_id)
            
            # 获取视频详细信息
            video_info = self.get_video_info(video_id)
            
            # 判断是否为主评论
            parent_comment_id = str(row.get('parent_comment_id', ''))
            is_main_comment = (parent_comment_id == '' or parent_comment_id == '0')
            
            # 清理和转换数据
            doc = {
                'id': str(row.get('id', '')),
                'user_id': str(row.get('user_id', '')),  # 这是评论者的ID
                'nickname': str(row.get('nickname', '')),
                'avatar': str(row.get('avatar', '')),
                'add_ts': self.convert_timestamp(row.get('add_ts')),
                'last_modify_ts': self.convert_timestamp(row.get('last_modify_ts')),
                'comment_id': str(row.get('comment_id', '')),
                'video_id': video_id,  # 这是视频的ID
                'content': str(row.get('content', '')),
                'create_time': self.convert_timestamp(row.get('create_time')),
                'sub_comment_count': self.safe_int(row.get('sub_comment_count', 0)),
                'parent_comment_id': parent_comment_id,
                'like_count': self.safe_int(row.get('like_count', 0)),
                'project_id': project_id,  # 基于视频的项目，而不是评论者的项目
                
                # 添加视频相关信息
                'video_title': video_info.get('video_title', ''),
                'video_url': video_info.get('video_url', ''),
                'video_uploader_nickname': video_info.get('video_uploader_nickname', ''),
                'video_uploader_uid': video_info.get('video_uploader_uid', ''),
                
                # 添加评论类型标识
                'is_main_comment': is_main_comment
            }
            
            # 构建批量插入数据
            bulk_data.append({
                '_index': self.es_service.comment_index,
                '_id': doc['comment_id'],  # 使用comment_id作为文档ID实现去重
                '_source': doc
            })
        
        # 批量插入Elasticsearch
        if bulk_data:
            self.bulk_insert(bulk_data)
    
    def import_account_data(self):
        """导入账号数据（可选功能）"""
        account_file = '账号大整合3.2xlsx_已提取UID.csv'
        
        if os.path.exists(account_file):
            print(f"正在处理账号文件: {account_file}")
            
            # 这里可以提取账号信息并关联到视频/评论数据
            # 或者作为独立的账号索引存储
            df = pd.read_csv(account_file, low_memory=False)
            
            # 处理账号数据逻辑...
            print(f"账号数据总数: {len(df)}")
    
    def convert_timestamp(self, timestamp):
        """转换时间戳，统一转换为秒级时间戳"""
        if pd.isna(timestamp) or timestamp == '':
            return None
        
        try:
            # 尝试不同的时间戳格式
            if isinstance(timestamp, str):
                timestamp = timestamp.strip()
                if timestamp == '' or timestamp == 'nan':
                    return None
                    
                # 处理字符串时间戳
                if len(timestamp) == 13:  # 毫秒时间戳
                    return int(int(timestamp) // 1000)  # 转换为秒
                elif len(timestamp) == 10:  # 秒时间戳
                    return int(timestamp)
                else:
                    # 尝试解析日期字符串
                    dt = pd.to_datetime(timestamp)
                    return int(dt.timestamp())
            else:
                # 数字时间戳
                timestamp = int(timestamp)
                if timestamp > 1e12:  # 毫秒时间戳
                    return int(timestamp // 1000)  # 转换为秒
                else:  # 秒时间戳
                    return timestamp
        except Exception as e:
            print(f"时间戳转换失败: {timestamp}, 错误: {e}")
            return None
    
    def safe_int(self, value):
        """安全转换为整数"""
        if pd.isna(value) or value == '':
            return 0
        try:
            return int(float(value))
        except:
            return 0
    
    def bulk_insert(self, bulk_data):
        """批量插入Elasticsearch"""
        if not bulk_data:
            return
        
        try:
            from elasticsearch.helpers import bulk
            success, failed = bulk(
                self.es_service.es,
                bulk_data,
                index=None,  # 每个文档都有自己的索引
                chunk_size=1000,
                request_timeout=60
            )
            print(f"成功插入: {success} 条, 失败: {len(failed)} 条")
            
            if failed:
                print(f"失败的文档: {failed[:5]}")  # 只打印前5个失败的文档
                
        except Exception as e:
            print(f"批量插入失败: {str(e)}")
            raise 

    def get_video_info(self, video_id):
        """根据视频ID获取视频详细信息"""
        if hasattr(self, 'video_info_mapping'):
            return self.video_info_mapping.get(str(video_id), {
                'video_title': '',
                'video_url': '',
                'video_uploader_nickname': '',
                'video_uploader_uid': ''
            })
        else:
            return {
                'video_title': '',
                'video_url': '',
                'video_uploader_nickname': '',
                'video_uploader_uid': ''
            }

    def clear_data(self, data_type='all'):
        """清空数据"""
        try:
            if data_type in ['videos', 'all']:
                print(f"🗑️ 清空视频索引...")
                self.es_service.es.indices.delete(index=self.es_service.video_index, ignore=[400, 404])
                print(f"✅ 视频索引已清空")
            
            if data_type in ['comments', 'all']:
                print(f"🗑️ 清空评论索引...")
                self.es_service.es.indices.delete(index=self.es_service.comment_index, ignore=[400, 404])
                print(f"✅ 评论索引已清空")
            
            # 重新创建索引
            if data_type in ['videos', 'comments', 'all']:
                self.es_service.create_indices()
                print(f"✅ 索引重新创建完成")
            
            return True
        except Exception as e:
            print(f"❌ 清空数据失败: {str(e)}")
            return False
    
    def get_data_statistics(self):
        """获取数据统计信息"""
        try:
            es = self.es_service.get_es_client()
            
            # 获取视频统计
            try:
                video_response = es.count(index=self.es_service.video_index)
                video_count = video_response.get('count', 0)
            except:
                video_count = 0
            
            # 获取评论统计
            try:
                comment_response = es.count(index=self.es_service.comment_index)
                comment_count = comment_response.get('count', 0)
            except:
                comment_count = 0
            
            # 获取项目统计
            try:
                projects = self.es_service.get_available_projects({'role': 'admin'})
                project_count = len(projects)
            except:
                project_count = 0
            
            return {
                'videos': video_count,
                'comments': comment_count,
                'projects': project_count,
                'total': video_count + comment_count
            }
        except Exception as e:
            print(f"❌ 获取统计信息失败: {str(e)}")
            return {
                'videos': 0,
                'comments': 0,
                'projects': 0,
                'total': 0
            }
    
    def handle_uploaded_file(self, file, file_type):
        """处理上传的文件"""
        try:
            import tempfile
            import shutil
            
            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, file.filename)
            
            # 保存文件
            file.save(file_path)
            print(f"📁 文件已保存到: {file_path}")
            
            # 根据文件类型处理
            if file_type == 'account':
                result = self.process_account_file(file_path)
            elif file_type == 'video':
                result = self.process_video_file(file_path)
            elif file_type == 'comment':
                result = self.process_comment_file(file_path)
            else:
                return {'success': False, 'message': '不支持的文件类型'}
            
            # 清理临时文件
            shutil.rmtree(temp_dir)
            
            return result
        except Exception as e:
            print(f"❌ 处理上传文件失败: {str(e)}")
            return {'success': False, 'message': f'处理文件失败: {str(e)}'}
    
    def process_account_file(self, file_path):
        """处理账号文件"""
        try:
            import shutil
            # 移动文件到工作目录
            target_path = '账号大整合3.2xlsx_已提取UID.csv'
            shutil.copy2(file_path, target_path)
            
            # 重新加载用户项目映射
            self.user_project_mapping = None
            self.load_user_project_mapping()
            
            return {
                'success': True, 
                'message': f'账号文件处理完成，共加载 {len(self.user_project_mapping)} 个用户映射'
            }
        except Exception as e:
            return {'success': False, 'message': f'处理账号文件失败: {str(e)}'}
    
    def process_video_file(self, file_path):
        """处理视频文件"""
        try:
            import shutil
            # 移动文件到目标位置
            target_dir = '1747748467790_dbexport_209215447'
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            target_path = os.path.join(target_dir, '2025-05-20-21-41-08_EXPORT_CSV_19274722_345_bilibili_video_0.csv')
            shutil.copy2(file_path, target_path)
            
            # 导入视频数据
            self.import_videos()
            
            return {'success': True, 'message': '视频文件处理完成'}
        except Exception as e:
            return {'success': False, 'message': f'处理视频文件失败: {str(e)}'}
    
    def process_comment_file(self, file_path):
        """处理评论文件"""
        try:
            import shutil
            # 移动文件到目标位置
            target_dir = '1747748467790_dbexport_209215447'
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            target_path = os.path.join(target_dir, '2025-05-20-21-41-11_EXPORT_CSV_19274722_637_bilibili_video_comment_1.csv')
            shutil.copy2(file_path, target_path)
            
            # 导入评论数据
            self.import_comments()
            
            return {'success': True, 'message': '评论文件处理完成'}
        except Exception as e:
            return {'success': False, 'message': f'处理评论文件失败: {str(e)}'}
    
    def get_visualization_statistics(self, params):
        """获取数据可视化统计信息"""
        try:
            es = self.es_service.get_es_client()
            
            # 解析参数
            project_id = params.get('project_id')
            time_range = params.get('time_range')  # 不设置默认值
            start_time = params.get('start_time')
            end_time = params.get('end_time')
            
            # 构建时间查询条件
            time_query = {}
            now = datetime.now()
            
            if start_time and end_time:
                time_query = {
                    "range": {
                        "create_time": {
                            "gte": int(start_time),
                            "lte": int(end_time)
                        }
                    }
                }
            elif time_range and time_range != 'custom':  # 只有明确指定时间范围时才应用
                days = int(time_range.replace('d', ''))
                start_timestamp = int((now - timedelta(days=days)).timestamp())
                time_query = {
                    "range": {
                        "create_time": {
                            "gte": start_timestamp
                        }
                    }
                }
            
            # 构建项目查询条件
            project_query = {}
            if project_id:
                project_query = {"term": {"project_id": project_id}}
            
            # 构建基础查询
            base_query = {"bool": {"must": []}}
            if time_query:
                base_query["bool"]["must"].append(time_query)
            if project_query:
                base_query["bool"]["must"].append(project_query)
            
            # 1. 播放量统计
            play_stats = self._get_play_stats(es, base_query)
            
            # 2. 时间段统计
            time_period_stats = self._get_time_period_stats(es, project_id)
            
            # 3. 爆文率统计
            viral_stats = self._get_viral_stats(es, base_query, project_id)
            
            # 4. 项目分布统计
            project_stats = self._get_project_distribution(es, time_query)
            
            return {
                'play_stats': play_stats,
                'time_period_stats': time_period_stats,
                'viral_stats': viral_stats,
                'project_stats': project_stats,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ 获取可视化统计失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def _get_play_stats(self, es, base_query):
        """获取播放量统计 - 改为按项目的播放总量统计"""
        try:
            response = es.search(
                index=self.es_service.video_index,
                body={
                    "query": base_query,
                    "aggs": {
                        "total_plays": {"sum": {"field": "video_play_count"}},
                        "avg_plays": {"avg": {"field": "video_play_count"}},
                        "max_plays": {"max": {"field": "video_play_count"}},
                        "by_project": {
                            "terms": {"field": "project_id", "size": 50},
                            "aggs": {
                                "total_plays": {"sum": {"field": "video_play_count"}},
                                "video_count": {"value_count": {"field": "video_id"}}
                            }
                        }
                    },
                    "size": 0
                }
            )
            
            aggs = response['aggregations']
            
            # 构建项目播放量数据
            project_data = []
            project_names = []
            play_values = []
            
            for bucket in aggs['by_project']['buckets']:
                project_name = bucket['key']
                total_plays = int(bucket['total_plays']['value'] or 0)
                video_count = bucket['video_count']['value']
                
                project_data.append({
                    'name': project_name,
                    'total_plays': total_plays,
                    'video_count': video_count,
                    'avg_plays': int(total_plays / video_count) if video_count > 0 else 0
                })
                project_names.append(project_name)
                play_values.append(total_plays)
            
            # 按播放量排序
            project_data.sort(key=lambda x: x['total_plays'], reverse=True)
            
            return {
                'total_plays': int(aggs['total_plays']['value'] or 0),
                'avg_plays': int(aggs['avg_plays']['value'] or 0),
                'max_plays': int(aggs['max_plays']['value'] or 0),
                'project_data': project_data
            }
        except Exception as e:
            print(f"获取播放量统计失败: {e}")
            return {'total_plays': 0, 'avg_plays': 0, 'max_plays': 0, 'project_data': []}
    
    def _get_time_period_stats(self, es, project_id=None):
        """获取不同时间段的统计"""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        periods = {
            '1d': now - timedelta(days=1),
            '7d': now - timedelta(days=7),
            '30d': now - timedelta(days=30)
        }
        
        stats = {}
        
        for period, start_time in periods.items():
            query = {
                "bool": {
                    "must": [
                        {"range": {"create_time": {"gte": int(start_time.timestamp())}}}
                    ]
                }
            }
            
            if project_id:
                query["bool"]["must"].append({"term": {"project_id": project_id}})
            
            try:
                response = es.count(
                    index=self.es_service.video_index,
                    body={"query": query}
                )
                stats[period] = response['count']
            except:
                stats[period] = 0
        
        return stats
    
    def _get_viral_stats(self, es, base_query, project_id=None):
        """获取爆文率统计（播放量>1000为爆文）"""
        try:
            # 总视频数
            total_response = es.search(
                index=self.es_service.video_index,
                body={"query": base_query, "size": 0}
            )
            total_videos = total_response['hits']['total']['value']
            
            # 爆文数（播放量>1000）
            viral_query = {
                "bool": {
                    "must": base_query["bool"]["must"] + [
                        {"range": {"video_play_count": {"gt": 1000}}}
                    ]
                }
            }
            
            viral_response = es.search(
                index=self.es_service.video_index,
                body={"query": viral_query, "size": 0}
            )
            viral_videos = viral_response['hits']['total']['value']
            
            # 各项目爆文率
            project_viral_stats = {}
            if not project_id:  # 只有在不限定项目时才统计各项目
                project_agg_response = es.search(
                    index=self.es_service.video_index,
                    body={
                        "query": base_query,
                        "aggs": {
                            "by_project": {
                                "terms": {"field": "project_id", "size": 100},
                                "aggs": {
                                    "viral_videos": {
                                        "filter": {"range": {"video_play_count": {"gt": 1000}}}
                                    }
                                }
                            }
                        },
                        "size": 0
                    }
                )
                
                for bucket in project_agg_response['aggregations']['by_project']['buckets']:
                    project_name = bucket['key']
                    total_project_videos = bucket['doc_count']
                    viral_project_videos = bucket['viral_videos']['doc_count']
                    viral_rate = (viral_project_videos / total_project_videos * 100) if total_project_videos > 0 else 0
                    
                    project_viral_stats[project_name] = {
                        'total': total_project_videos,
                        'viral': viral_project_videos,
                        'rate': round(viral_rate, 2)
                    }
            
            overall_viral_rate = (viral_videos / total_videos * 100) if total_videos > 0 else 0
            
            return {
                'total_videos': total_videos,
                'viral_videos': viral_videos,
                'viral_rate': round(overall_viral_rate, 2),
                'project_stats': project_viral_stats
            }
            
        except Exception as e:
            print(f"获取爆文率统计失败: {e}")
            return {'total_videos': 0, 'viral_videos': 0, 'viral_rate': 0, 'project_stats': {}}
    
    def _get_project_distribution(self, es, time_query=None):
        """获取项目分布统计"""
        try:
            query = {"bool": {"must": []}}
            if time_query:
                query["bool"]["must"].append(time_query)
            
            response = es.search(
                index=self.es_service.video_index,
                body={
                    "query": query,
                    "aggs": {
                        "by_project": {
                            "terms": {"field": "project_id", "size": 100},
                            "aggs": {
                                "total_plays": {"sum": {"field": "video_play_count"}}
                            }
                        }
                    },
                    "size": 0
                }
            )
            
            project_data = []
            for bucket in response['aggregations']['by_project']['buckets']:
                project_data.append({
                    'name': bucket['key'],
                    'video_count': bucket['doc_count'],
                    'total_plays': int(bucket['total_plays']['value'] or 0)
                })
            
            return sorted(project_data, key=lambda x: x['video_count'], reverse=True)
            
        except Exception as e:
            print(f"获取项目分布失败: {e}")
            return [] 
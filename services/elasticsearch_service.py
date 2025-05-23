from elasticsearch import Elasticsearch
from datetime import datetime
import os
import jieba
import json

class ElasticsearchService:
    def __init__(self):
        # 延迟初始化，避免启动时连接问题
        self.es = None
        self.es_host = os.getenv('ELASTICSEARCH_HOST', 'localhost')
        self.es_port = int(os.getenv('ELASTICSEARCH_PORT', 9200))
        self.es_user = os.getenv('ELASTICSEARCH_USER')
        self.es_password = os.getenv('ELASTICSEARCH_PASSWORD')
        
        self.video_index = 'videos_search'
        self.comment_index = 'comments_search'
    
    def get_es_client(self):
        """获取Elasticsearch客户端，懒加载"""
        if self.es is None:
            try:
                # 使用更简单的连接方式
                if self.es_user and self.es_password:
                    self.es = Elasticsearch(
                        f"http://{self.es_host}:{self.es_port}",
                        basic_auth=(self.es_user, self.es_password),
                        verify_certs=False,
                        request_timeout=30
                    )
                else:
                    self.es = Elasticsearch(
                        f"http://{self.es_host}:{self.es_port}",
                        verify_certs=False,
                        request_timeout=30
                    )
                
                # 测试连接
                self.es.info()
                
            except Exception as e:
                print(f"Elasticsearch连接失败: {str(e)}")
                # 返回一个模拟客户端，避免应用崩溃
                self.es = MockElasticsearchClient()
        
        return self.es

    def create_indices(self):
        """创建Elasticsearch索引"""
        es = self.get_es_client()
        
        # 视频索引映射
        video_mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    "nickname": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "avatar": {"type": "keyword"},
                    "add_ts": {"type": "date", "format": "epoch_millis"},
                    "last_modify_ts": {"type": "date", "format": "epoch_millis"},
                    "video_id": {"type": "keyword"},
                    "video_type": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "desc": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "create_time": {"type": "long"},
                    "liked_count": {"type": "integer"},
                    "video_play_count": {"type": "integer"},
                    "video_danmaku": {"type": "integer"},
                    "video_comment": {"type": "integer"},
                    "video_url": {"type": "keyword"},
                    "video_cover_url": {"type": "keyword"},
                    "source_keyword": {"type": "text"},
                    "project_id": {"type": "keyword"}
                }
            }
        }
        
        # 评论索引映射  
        comment_mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    "nickname": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "avatar": {"type": "keyword"},
                    "add_ts": {"type": "date", "format": "epoch_millis"},
                    "last_modify_ts": {"type": "date", "format": "epoch_millis"},
                    "comment_id": {"type": "keyword"},
                    "video_id": {"type": "keyword"},
                    "content": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "create_time": {"type": "long"},
                    "sub_comment_count": {"type": "integer"},
                    "parent_comment_id": {"type": "keyword"},
                    "like_count": {"type": "integer"},
                    "project_id": {"type": "keyword"},
                    # 视频相关字段
                    "video_title": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "video_url": {"type": "keyword"},
                    "video_uploader_nickname": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "video_uploader_uid": {"type": "keyword"},
                    # 评论类型标识
                    "is_main_comment": {"type": "boolean"}
                }
            }
        }
        
        # 创建索引
        try:
            if not es.indices.exists(index=self.video_index):
                es.indices.create(index=self.video_index, body=video_mapping)
                
            if not es.indices.exists(index=self.comment_index):
                es.indices.create(index=self.comment_index, body=comment_mapping)
        except Exception as e:
            print(f"创建索引失败: {str(e)}")
    
    def search_videos(self, search_params, current_user):
        """搜索视频"""
        es = self.get_es_client()
        
        query = {
            "bool": {
                "must": [],
                "filter": []
            }
        }
        
        # 关键词搜索
        keywords = search_params.get('keywords', '')
        if keywords:
            keyword_query = {
                "multi_match": {
                    "query": keywords,
                    "fields": ["title^2", "desc", "nickname"],
                    "type": "best_fields",
                    "operator": "or"
                }
            }
            query["bool"]["must"].append(keyword_query)
        
        # 视频标题搜索
        video_title = search_params.get('video_title', '')
        if video_title:
            query["bool"]["must"].append({
                "match": {
                    "title": video_title
                }
            })
        
        # UP主昵称搜索
        uploader_nickname = search_params.get('uploader_nickname', '')
        if uploader_nickname:
            query["bool"]["must"].append({
                "match": {
                    "nickname": uploader_nickname
                }
            })
        
        # UP主UID搜索
        uploader_uid = search_params.get('uploader_uid', '')
        if uploader_uid:
            query["bool"]["filter"].append({
                "term": {
                    "user_id": uploader_uid
                }
            })
        
        # 项目筛选
        project_id = search_params.get('project_id')
        if project_id:
            query["bool"]["filter"].append({
                "term": {
                    "project_id": project_id
                }
            })
        
        # 时间范围筛选
        time_range = search_params.get('time_range')
        if time_range and isinstance(time_range, dict):
            start_time = time_range.get('start')
            end_time = time_range.get('end')
            if start_time or end_time:
                print(f"🕐 时间范围查询: start={start_time}, end={end_time}")
                range_query = {"range": {"create_time": {}}}
                if start_time:
                    start_timestamp = int(start_time)
                    range_query["range"]["create_time"]["gte"] = start_timestamp
                    print(f"   开始时间戳: {start_timestamp}")
                if end_time:
                    end_timestamp = int(end_time)
                    range_query["range"]["create_time"]["lte"] = end_timestamp
                    print(f"   结束时间戳: {end_timestamp}")
                query["bool"]["filter"].append(range_query)
                print(f"   时间查询条件: {range_query}")
        
        # 如果没有任何查询条件，使用match_all
        if not query["bool"]["must"] and not query["bool"]["filter"]:
            query = {"match_all": {}}
        
        # 权限控制
        if current_user['role'] != 'admin':
            project_access = current_user.get('project_access', [])
            if project_access:
                if query == {"match_all": {}}:
                    query = {"bool": {"filter": []}}
                elif "filter" not in query["bool"]:
                    query["bool"]["filter"] = []
                query["bool"]["filter"].append({
                    "terms": {
                        "project_id": project_access
                    }
                })
        
        # 排序
        sort_by = search_params.get('sort_by', 'create_time')
        sort_order = search_params.get('sort_order', 'desc')
        
        # 映射前端字段到ES字段
        sort_field_map = {
            'create_time': 'create_time',
            'video_play_count': 'video_play_count'
        }
        
        es_sort_field = sort_field_map.get(sort_by, 'create_time')
        sort = [{es_sort_field: {"order": sort_order}}]
        
        # 分页
        page = search_params.get('page', 1)
        page_size = search_params.get('page_size', 20)
        from_param = (page - 1) * page_size
        
        # 高亮设置
        highlight = {
            "fields": {
                "title": {},
                "desc": {}
            },
            "pre_tags": ["<em>"],
            "post_tags": ["</em>"]
        }
        
        try:
            # 执行搜索
            response = es.search(
                index=self.video_index,
                body={
                    "query": query,
                    "from": from_param,
                    "size": page_size,
                    "sort": sort,
                    "highlight": highlight
                }
            )
            
            # 处理结果
            hits = response['hits']['hits']
            total = response['hits']['total']['value']
            
            results = []
            for hit in hits:
                result = hit['_source']
                result['_id'] = hit['_id']
                # 添加高亮信息
                if 'highlight' in hit:
                    result['highlight'] = hit['highlight']
                results.append(result)
            
            return {
                'results': results,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
            
        except Exception as e:
            print(f"搜索失败: {str(e)}")
            return {
                'results': [],
                'total': 0,
                'page': page,
                'page_size': page_size,
                'total_pages': 0
            }
    
    def search_comments(self, search_params, current_user):
        """搜索评论"""
        es = self.get_es_client()
        
        query = {
            "bool": {
                "must": [],
                "filter": []
            }
        }
        
        # 关键词搜索
        keywords = search_params.get('keywords', '')
        if keywords:
            query["bool"]["must"].append({
                "match": {
                    "content": keywords
                }
            })
        
        # 评论者UID搜索
        commenter_uid = search_params.get('commenter_uid', '')
        if commenter_uid:
            query["bool"]["filter"].append({
                "term": {
                    "user_id": commenter_uid
                }
            })
        
        # 评论者昵称搜索
        commenter_nickname = search_params.get('commenter_nickname', '')
        if commenter_nickname:
            query["bool"]["must"].append({
                "match": {
                    "nickname": commenter_nickname
                }
            })
        
        # 项目筛选
        project_id = search_params.get('project_id')
        if project_id:
            query["bool"]["filter"].append({
                "term": {
                    "project_id": project_id
                }
            })
        
        # 时间范围筛选
        time_range = search_params.get('time_range')
        if time_range and isinstance(time_range, dict):
            start_time = time_range.get('start')
            end_time = time_range.get('end')
            if start_time or end_time:
                print(f"🕐 评论时间范围查询: start={start_time}, end={end_time}")
                range_query = {"range": {"create_time": {}}}
                if start_time:
                    start_timestamp = int(start_time)
                    range_query["range"]["create_time"]["gte"] = start_timestamp
                    print(f"   开始时间戳: {start_timestamp}")
                if end_time:
                    end_timestamp = int(end_time)
                    range_query["range"]["create_time"]["lte"] = end_timestamp
                    print(f"   结束时间戳: {end_timestamp}")
                query["bool"]["filter"].append(range_query)
                print(f"   时间查询条件: {range_query}")
        
        # 如果没有任何查询条件，使用match_all
        if not query["bool"]["must"] and not query["bool"]["filter"]:
            query = {"match_all": {}}
        
        # 权限控制
        if current_user['role'] != 'admin':
            project_access = current_user.get('project_access', [])
            if project_access:
                if query == {"match_all": {}}:
                    query = {"bool": {"filter": []}}
                elif "filter" not in query["bool"]:
                    query["bool"]["filter"] = []
                query["bool"]["filter"].append({
                    "terms": {
                        "project_id": project_access
                    }
                })
        
        # 排序
        sort_by = search_params.get('sort_by', 'create_time')
        sort_order = search_params.get('sort_order', 'desc')
        
        # 映射前端字段到ES字段
        sort_field_map = {
            'create_time': 'create_time',
            'like_count': 'like_count'
        }
        
        es_sort_field = sort_field_map.get(sort_by, 'create_time')
        sort = [{es_sort_field: {"order": sort_order}}]
        
        # 分页
        page = search_params.get('page', 1)
        page_size = search_params.get('page_size', 20)
        from_param = (page - 1) * page_size
        
        # 高亮设置
        highlight = {
            "fields": {
                "content": {}
            },
            "pre_tags": ["<em>"],
            "post_tags": ["</em>"]
        }
        
        try:
            # 执行搜索
            response = es.search(
                index=self.comment_index,
                body={
                    "query": query,
                    "from": from_param,
                    "size": page_size,
                    "sort": sort,
                    "highlight": highlight
                }
            )
            
            # 处理结果
            hits = response['hits']['hits']
            total = response['hits']['total']['value']
            
            results = []
            for hit in hits:
                result = hit['_source']
                result['_id'] = hit['_id']
                # 添加高亮信息
                if 'highlight' in hit:
                    result['highlight'] = hit['highlight']
                
                # 如果不是主评论，获取父评论信息
                if not result.get('is_main_comment', True) and result.get('parent_comment_id'):
                    parent_info = self.get_parent_comment_info(result['parent_comment_id'])
                    result['parent_comment_info'] = parent_info
                
                results.append(result)
            
            return {
                'results': results,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
            
        except Exception as e:
            print(f"搜索失败: {str(e)}")
            return {
                'results': [],
                'total': 0,
                'page': page,
                'page_size': page_size,
                'total_pages': 0
            }
    
    def get_parent_comment_info(self, parent_comment_id):
        """获取父评论信息"""
        es = self.get_es_client()
        
        try:
            # 通过comment_id查找父评论
            response = es.search(
                index=self.comment_index,
                body={
                    "query": {
                        "term": {
                            "comment_id": parent_comment_id
                        }
                    },
                    "size": 1
                }
            )
            
            if response['hits']['hits']:
                parent_comment = response['hits']['hits'][0]['_source']
                return {
                    'nickname': parent_comment.get('nickname', ''),
                    'content': parent_comment.get('content', ''),
                    'create_time': parent_comment.get('create_time', ''),
                    'like_count': parent_comment.get('like_count', 0)
                }
            else:
                return {
                    'nickname': '已删除用户',
                    'content': '评论已删除',
                    'create_time': '',
                    'like_count': 0
                }
                
        except Exception as e:
            print(f"获取父评论信息失败: {str(e)}")
            return {
                'nickname': '获取失败',
                'content': '无法获取父评论信息',
                'create_time': '',
                'like_count': 0
            }
    
    def find_similar_comments(self, comment_id, current_user):
        """查找相似评论"""
        es = self.get_es_client()
        
        return {
            'source_comment': {'content': '示例评论'},
            'similar_comments': []
        }
    
    def get_time_range(self, data_type):
        """获取指定数据类型的时间范围"""
        es = self.get_es_client()
        
        index = self.video_index if data_type == 'videos' else self.comment_index
        
        try:
            response = es.search(
                index=index,
                body={
                    'size': 0,
                    'aggs': {
                        'time_stats': {
                            'stats': {
                                'field': 'create_time'
                            }
                        }
                    }
                }
            )
            
            if 'aggregations' in response and 'time_stats' in response['aggregations']:
                stats = response['aggregations']['time_stats']
                return {
                    'min': int(stats['min']),
                    'max': int(stats['max']),
                    'count': int(stats['count'])
                }
            else:
                return {'min': 0, 'max': 0, 'count': 0}
                
        except Exception as e:
            print(f"获取时间范围失败: {str(e)}")
            return {'min': 0, 'max': 0, 'count': 0}

    def get_available_projects(self, current_user):
        """获取用户可访问的项目列表"""
        es = self.get_es_client()
        
        try:
            # 获取所有项目的视频数量统计
            video_stats = es.search(
                index=self.video_index,
                body={
                    "size": 0,
                    "aggs": {
                        "projects": {
                            "terms": {
                                "field": "project_id",
                                "size": 100  # 获取最多100个项目
                            }
                        }
                    }
                }
            )
            
            # 获取所有项目的评论数量统计
            comment_stats = es.search(
                index=self.comment_index,
                body={
                    "size": 0,
                    "aggs": {
                        "projects": {
                            "terms": {
                                "field": "project_id",
                                "size": 100
                            }
                        }
                    }
                }
            )
            
            # 合并统计信息
            project_data = {}
            
            # 处理视频数据
            if 'aggregations' in video_stats and 'projects' in video_stats['aggregations']:
                for bucket in video_stats['aggregations']['projects']['buckets']:
                    project_id = bucket['key']
                    video_count = bucket['doc_count']
                    project_data[project_id] = {
                        'id': project_id,
                        'name': project_id,
                        'video_count': video_count,
                        'comment_count': 0
                    }
            
            # 处理评论数据
            if 'aggregations' in comment_stats and 'projects' in comment_stats['aggregations']:
                for bucket in comment_stats['aggregations']['projects']['buckets']:
                    project_id = bucket['key']
                    comment_count = bucket['doc_count']
                    if project_id in project_data:
                        project_data[project_id]['comment_count'] = comment_count
                    else:
                        project_data[project_id] = {
                            'id': project_id,
                            'name': project_id,
                            'video_count': 0,
                            'comment_count': comment_count
                        }
            
            # 转换为列表格式
            projects = []
            for project_id, data in project_data.items():
                total_docs = data['video_count'] + data['comment_count']
                
                # 权限控制：普通用户只能看到有权限的项目
                if current_user['role'] != 'admin':
                    project_access = current_user.get('project_access', [])
                    if project_id not in project_access:
                        continue
                
                projects.append({
                    'id': project_id,
                    'name': project_id,
                    'doc_count': total_docs,
                    'video_count': data['video_count'],
                    'comment_count': data['comment_count']
                })
            
            # 按文档数量降序排序
            projects.sort(key=lambda x: x['doc_count'], reverse=True)
            
            return projects
            
        except Exception as e:
            print(f"获取项目列表失败: {str(e)}")
            # 发生错误时返回默认项目列表
            default_projects = [
                {'id': '巨书', 'name': '巨书', 'doc_count': 0, 'video_count': 0, 'comment_count': 0},
                {'id': '康江文', 'name': '康江文', 'doc_count': 0, 'video_count': 0, 'comment_count': 0}
            ]
            
            # 对于普通用户，过滤项目权限
            if current_user['role'] != 'admin':
                project_access = current_user.get('project_access', [])
                default_projects = [p for p in default_projects if p['id'] in project_access]
            
            return default_projects


class MockElasticsearchClient:
    """模拟Elasticsearch客户端，用于在ES不可用时避免应用崩溃"""
    
    def __init__(self):
        self.options = MockOptions()
        self.transport = MockTransport()
    
    def info(self):
        return {"version": {"number": "mock"}}
    
    def indices(self):
        return MockIndices()
    
    def search(self, **kwargs):
        return {
            'hits': {
                'hits': [],
                'total': {'value': 0}
            }
        }
    
    def count(self, **kwargs):
        return {'count': 0}
    
    def index(self, **kwargs):
        return {'_id': 'mock_id', 'result': 'created'}
    
    def bulk(self, **kwargs):
        # 模拟bulk操作成功
        return {
            'errors': False,
            'items': []
        }


class MockOptions:
    def __init__(self):
        self.request_timeout = 30


class MockTransport:
    def __init__(self):
        self.hosts = [{'host': 'localhost', 'port': 9200}]


class MockIndices:
    def exists(self, **kwargs):
        return False
    
    def create(self, **kwargs):
        pass
    
    def delete(self, **kwargs):
        pass 
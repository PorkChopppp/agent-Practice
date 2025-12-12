"""
知识管理代理模块

知识管理代理（Knowledge Management Agent）负责管理和维护知识库，
包括知识的增删改查、知识图谱构建、以及与其他代理的协作。
"""

import json
from datetime import datetime
from typing import List, Dict, Any
from database.milvus_client import MilvusClient
from database.postgres_client import PostgresClient

class KnowledgeAgent:
    """
    知识管理代理类
    
    负责知识的管理、维护和检索，提供高级的知识库操作功能。
    """
    
    def __init__(self, use_milvus=True):
        """
        初始化知识管理代理
        
        Args:
            use_milvus (bool): 是否使用Milvus向量数据库
        """
        self.milvus_client = MilvusClient(use_milvus=use_milvus)
        self.postgres_client = PostgresClient()
        print("知识管理代理初始化完成")
    
    def add_knowledge(self, content: str, metadata: Dict[str, Any] = None) -> bool:
        """
        添加知识到知识库
        
        Args:
            content (str): 知识内容
            metadata (dict): 元数据，如来源、类别、标签等
            
        Returns:
            bool: 添加是否成功
        """
        try:
            # 生成嵌入向量（这里简化处理，实际应该使用嵌入模型）
            embedding = [0.0] * 1024  # 使用1024维向量匹配bge模型
            
            # 构造来源信息
            source = metadata.get("source", "unknown") if metadata else "unknown"
            
            # 插入到Milvus
            self.milvus_client.insert_document(
                content=content,
                embedding=embedding,
                source=source,
                timestamp=int(datetime.now().timestamp())
            )
            
            print(f"成功添加知识: {content[:50]}...")
            return True
        except Exception as e:
            print(f"添加知识时出错: {e}")
            return False
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        搜索相关知识
        
        Args:
            query (str): 查询内容
            limit (int): 返回结果数量限制
            
        Returns:
            list: 相关知识列表
        """
        try:
            # 生成查询向量（这里简化处理）
            query_embedding = [0.0] * 1024
            
            # 从Milvus搜索相似文档
            results = self.milvus_client.search_similar_documents(query_embedding, limit)
            
            # 格式化结果
            knowledge_list = []
            for result in results:
                knowledge_list.append({
                    "content": result.entity.get("content"),
                    "source": result.entity.get("source"),
                    "timestamp": result.entity.get("timestamp")
                })
            
            return knowledge_list
        except Exception as e:
            print(f"搜索知识时出错: {e}")
            return []
    
    def update_knowledge(self, knowledge_id: int, content: str = None, metadata: Dict[str, Any] = None) -> bool:
        """
        更新知识库中的知识
        
        Args:
            knowledge_id (int): 知识ID
            content (str): 新的内容
            metadata (dict): 新的元数据
            
        Returns:
            bool: 更新是否成功
        """
        # 在当前实现中，Milvus不直接支持更新操作
        # 需要先删除再插入新记录
        print("知识更新功能需要在完整实现中添加")
        return False
    
    def delete_knowledge(self, knowledge_id: int) -> bool:
        """
        从知识库中删除知识
        
        Args:
            knowledge_id (int): 知识ID
            
        Returns:
            bool: 删除是否成功
        """
        # 在当前实现中，Milvus不直接支持删除操作
        print("知识删除功能需要在完整实现中添加")
        return False
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            dict: 统计信息
        """
        try:
            # 获取本地数据统计（简化实现）
            if hasattr(self.milvus_client, 'local_data'):
                total_knowledge = len(self.milvus_client.local_data)
                sources = set()
                for item in self.milvus_client.local_data:
                    sources.add(item.get("source", "unknown"))
                
                return {
                    "total_knowledge": total_knowledge,
                    "sources": list(sources),
                    "last_updated": datetime.now().isoformat()
                }
            else:
                return {
                    "total_knowledge": 0,
                    "sources": [],
                    "last_updated": datetime.now().isoformat()
                }
        except Exception as e:
            print(f"获取知识库统计时出错: {e}")
            return {}
    
    def build_knowledge_graph(self) -> Dict[str, Any]:
        """
        构建知识图谱
        
        Returns:
            dict: 知识图谱数据
        """
        # 简化实现，实际应该分析实体和关系
        return {
            "nodes": [],
            "edges": [],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
    
    def close(self):
        """
        关闭代理连接
        """
        try:
            self.milvus_client.close()
        except:
            pass
        try:
            self.postgres_client.close()
        except:
            pass
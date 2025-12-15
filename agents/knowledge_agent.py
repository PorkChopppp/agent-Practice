"""
知识管理代理模块（Knowledge Management Agent）

本模块处于【Agent / Service 层】：
- 对上：为 LLM / Agent / API 提供“知识增删查”等统一能力
- 对下：封装向量数据库（Milvus）和结构化数据库（PostgreSQL）

核心思想：
- Agent 不直接操作数据库
- 所有数据库细节都由 Client 层屏蔽
"""

import json  # 当前文件未使用，可在后续序列化知识图谱时使用
from datetime import datetime
from typing import List, Dict, Any

# 向量数据库客户端：负责 embedding + 相似度检索
from database.milvus_client import MilvusClient
# 结构化数据库客户端：用于元数据、关系、统计等（当前版本未深度使用）
from database.postgres_client import PostgresClient


class KnowledgeAgent:
    """
    知识管理代理（Knowledge Agent）

    职责定位：
    - 管理知识的生命周期（写入 / 检索 / 统计）
    - 作为 RAG / Agent 的“知识入口”
    - 不关心具体数据库实现细节
    """

    def __init__(self, use_milvus: bool = True):
        """
        初始化知识管理代理

        Args:
            use_milvus (bool):
                是否启用 Milvus 向量数据库
                - True ：真实向量检索
                - False：本地 mock / 调试模式
        """

        # 初始化向量数据库客户端
        # KnowledgeAgent 只调用接口，不关心连接方式、schema 等细节
        self.milvus_client = MilvusClient(use_milvus=use_milvus)

        # 初始化 PostgreSQL 客户端
        # 主要用于：结构化元数据、关系、统计信息等
        self.postgres_client = PostgresClient()

        print("知识管理代理初始化完成")

    def add_knowledge(self, content: str, metadata: Dict[str, Any] = None) -> bool:
        """
        添加一条知识到知识库

        这是典型的【RAG 写入流程】：
        1. 文本 → embedding
        2. embedding + 原文 + 元数据 → 向量库

        Args:
            content (str): 知识正文文本
            metadata (dict): 元数据（来源、标签、类别等）

        Returns:
            bool: 是否添加成功（对上层隐藏异常细节）
        """
        try:
            # =========================
            # 1. 生成文本向量（embedding）
            # =========================
            # 这里是【占位实现】：
            # - 使用 1024 维向量是为了匹配 bge / 通用嵌入模型
            # - 实际项目中应替换为真实 embedding 模型
            #
            # 例如：
            # embedding = embedding_model.encode(content)
            embedding = [0.0] * 1024

            # =========================
            # 2. 处理元数据
            # =========================
            # 防御式写法，避免 metadata 为 None
            source = metadata.get("source", "unknown") if metadata else "unknown"

            # =========================
            # 3. 写入 Milvus 向量数据库
            # =========================
            # KnowledgeAgent 不关心：
            # - collection 如何建
            # - 主键如何生成
            # - Milvus SDK 细节
            self.milvus_client.insert_document(
                content=content,
                embedding=embedding,
                source=source,
                timestamp=int(datetime.now().timestamp())
            )

            print(f"成功添加知识: {content[:50]}...")
            return True

        except Exception as e:
            # 对上层只暴露失败，不传播底层异常
            print(f"添加知识时出错: {e}")
            return False

    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        根据查询文本搜索相关知识

        这是典型的【RAG 读流程】：
        1. Query → embedding
        2. embedding → 向量相似度搜索
        3. 返回统一的业务数据结构

        Args:
            query (str): 查询文本
            limit (int): 返回结果数量上限

        Returns:
            List[Dict]: 知识列表（与数据库实现解耦）
        """
        try:
            # =========================
            # 1. 查询文本向量化（占位实现）
            # =========================
            query_embedding = [0.0] * 1024

            # =========================
            # 2. 向量相似度搜索
            # =========================
            results = self.milvus_client.search_similar_documents(
                query_embedding,
                limit
            )

            # =========================
            # 3. 格式化搜索结果
            # =========================
            # 屏蔽 Milvus SearchResult 的原始结构
            # 对上层统一返回“知识对象”
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

    def update_knowledge(
        self,
        knowledge_id: int,
        content: str = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        更新知识内容（当前为占位）

        说明：
        - Milvus 不支持直接 UPDATE
        - 正确做法是：
            1. 根据 ID 删除旧向量
            2. 插入新向量

        Args:
            knowledge_id (int): 知识唯一标识
            content (str): 新内容
            metadata (dict): 新元数据

        Returns:
            bool: 是否更新成功
        """
        print("知识更新功能需要在完整实现中添加")
        return False

    def delete_knowledge(self, knowledge_id: int) -> bool:
        """
        删除知识（当前为占位）

        Milvus 的删除通常依赖：
        - 主键
        - 或条件表达式

        Args:
            knowledge_id (int): 知识唯一标识

        Returns:
            bool: 是否删除成功
        """
        print("知识删除功能需要在完整实现中添加")
        return False

    def get_knowledge_stats(self) -> Dict[str, Any]:
        """
        获取知识库统计信息

        主要用途：
        - 调试
        - 可视化
        - 管理后台

        Returns:
            dict: 知识库统计结果
        """
        try:
            # 当使用本地 mock Milvus 时，直接从内存统计
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

            # 未启用或无数据时的兜底返回
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
        构建知识图谱（占位实现）

        设计意图：
        - 从知识中抽取实体与关系
        - 形成图结构供 Agent 推理使用

        Returns:
            dict: 知识图谱数据结构
        """
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
        关闭代理，释放底层资源

        设计原因：
        - Agent 生命周期 ≠ 进程生命周期
        - 在 FastAPI / LangGraph 中尤为重要
        """
        try:
            self.milvus_client.close()
        except Exception:
            pass

        try:
            self.postgres_client.close()
        except Exception:
            pass

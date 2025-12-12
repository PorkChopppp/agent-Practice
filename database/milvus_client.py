"""
Milvus向量数据库客户端模块

Milvus是一个专门用于存储和检索高维向量数据的数据库系统。
它特别适合AI应用场景，如语义搜索、推荐系统、图像识别等，
其中需要高效地存储大量向量并快速查找相似向量。

本模块实现了Milvus数据库的操作接口，同时提供了本地文件存储作为备选方案，
以保证即使在无法连接到Milvus服务器时也能正常运行。
"""

from config.settings import MILVUS_HOST, MILVUS_PORT
import numpy as np
import os
import json

class MilvusClient:
    """
    Milvus数据库客户端类
    
    负责与Milvus向量数据库交互，包括连接、创建集合、插入文档、
    搜索相似文档等功能。如果无法连接到Milvus服务器，则会自动
    切换到本地文件存储模式。
    """
    
    def __init__(self, use_milvus=None):
        """
        初始化Milvus客户端
        
        Args:
            use_milvus (bool, optional): 是否强制使用Milvus数据库。
                                         如果为None，则从配置文件读取设置。
        """
        # 如果未指定use_milvus，则从环境变量读取，如果没有则默认为False
        if use_milvus is None:
            from config.settings import USE_MILVUS
            self.use_milvus = USE_MILVUS
        else:
            self.use_milvus = use_milvus
            
        print(f"Milvus功能开关: {self.use_milvus}")
            
        if not self.use_milvus:
            print("Milvus功能已禁用，使用本地文件存储")
            # 设置本地存储文件路径
            self.storage_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'milvus_data.json')
            self._load_local_data()
            return
            
        # 尝试连接到Milvus数据库
        try:
            # 导入pymilvus库并建立连接
            from pymilvus import connections
            connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
            self.collection_name = "research_documents"  # 定义集合名称
            self.collection = None
            self._setup_collection()  # 设置集合
            print("成功连接到Milvus数据库")
        except Exception as e:
            # 连接失败时的错误处理
            print(f"无法连接到Milvus服务器: {e}")
            print("将禁用Milvus功能，使用模拟数据")
            self.use_milvus = False
            self.storage_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'milvus_data.json')
            self._load_local_data()

    def _load_local_data(self):
        """
        从本地文件加载数据
        
        当无法连接到Milvus数据库时，使用本地JSON文件存储数据。
        此方法在初始化时调用，加载已有数据。
        """
        self.local_data = []  # 初始化本地数据列表
        if os.path.exists(self.storage_file):
            try:
                # 尝试从JSON文件读取数据
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self.local_data = json.load(f)
            except Exception as e:
                # 文件读取失败时给出警告并初始化为空列表
                print(f"加载本地数据时出错: {e}")
                self.local_data = []

    def _save_local_data(self):
        """
        将数据保存到本地文件
        
        每次对本地数据进行修改后，都需要调用此方法将更改保存到磁盘。
        """
        try:
            # 将数据写入JSON文件
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.local_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存本地数据时出错: {e}")

    def _setup_collection(self):
        """
        设置Milvus集合
        
        在Milvus中，集合类似于关系数据库中的表，用于组织和存储数据。
        此方法负责创建集合、定义字段结构以及建立索引。
        """
        if not self.use_milvus:
            return
            
        try:
            # 导入必要的Milvus组件
            from pymilvus import utility, Collection, CollectionSchema, FieldSchema, DataType
            
            # 检查集合是否已存在
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
                print(f"使用现有集合: {self.collection_name}")
                return

            # 定义集合的字段结构
            fields = [
                # 主键字段，自动递增的整数ID
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                # 文档内容字段，存储原始文本
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
                # 向量嵌入字段，存储文本的向量表示
                # 使用1024维以匹配硅基流动的bge模型
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),
                # 来源字段，记录文档来源
                FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=256),
                # 时间戳字段，记录文档插入时间
                FieldSchema(name="timestamp", dtype=DataType.INT64)
            ]

            # 创建集合模式
            schema = CollectionSchema(fields, description="Research documents collection")
            
            # 创建集合并加载到内存中以提高查询性能
            self.collection = Collection(self.collection_name, schema)
            
            # 创建索引以加速向量相似性搜索
            # IVF_FLAT是一种常用的索引类型，适用于大多数场景
            # L2是欧几里得距离度量，用于计算向量间的相似性
            index_params = {
                "index_type": "IVF_FLAT",
                "metric_type": "L2",
                "params": {"nlist": 128}  # 聚类中心数量
            }
            
            self.collection.create_index(field_name="embedding", index_params=index_params)
            self.collection.load()  # 将集合加载到内存
            print("Milvus集合设置完成")
        except Exception as e:
            # 集合设置失败时回退到本地存储
            print(f"设置Milvus集合时出错: {e}")
            print("切换到本地存储模式")
            self.use_milvus = False
            self.storage_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'milvus_data.json')
            self._load_local_data()

    def insert_document(self, content, embedding, source, timestamp):
        """
        插入文档到数据库
        
        Args:
            content (str): 文档内容
            embedding (list): 文档的向量表示
            source (str): 文档来源
            timestamp (int): 插入时间戳
        """
        if self.use_milvus:
            try:
                # 构造要插入的数据格式
                data = [
                    [content],      # 内容字段
                    [embedding],    # 向量字段
                    [source],       # 来源字段
                    [timestamp]     # 时间戳字段
                ]
                
                # 执行插入操作并刷新以确保数据持久化
                self.collection.insert(data)
                self.collection.flush()
            except Exception as e:
                print(f"插入文档到Milvus时出错: {e}")
        else:
            # 使用本地存储方式
            doc = {
                "id": len(self.local_data) + 1,  # 分配唯一ID
                "content": content,
                "embedding": embedding,
                "source": source,
                "timestamp": timestamp
            }
            self.local_data.append(doc)
            self._save_local_data()  # 保存到本地文件

    def search_similar_documents(self, query_embedding, limit=5):
        """
        搜索相似文档
        
        使用向量相似性搜索找出与查询向量最相似的文档。
        
        Args:
            query_embedding (list): 查询向量
            limit (int): 返回结果的最大数量，默认为5
            
        Returns:
            list: 搜索结果列表
        """
        if self.use_milvus:
            try:
                from pymilvus import Collection
                search_params = {
                    "metric_type": "L2",
                    "params": {"nprobe": 10}
                }
                
                results = self.collection.search(
                    data=[query_embedding],
                    anns_field="embedding",
                    param=search_params,
                    limit=limit,
                    output_fields=["content", "source", "timestamp"]
                )
                
                return results[0]
            except Exception as e:
                print(f"从Milvus搜索文档时出错: {e}")
                # 回退到本地数据
                return self._search_local_documents(limit)
        else:
            # 使用本地数据搜索
            return self._search_local_documents(limit)
    
    def _search_local_documents(self, limit=5):
        """
        在本地数据中搜索文档
        
        这是一个简化的搜索实现，在实际应用中应该实现基于向量相似度的搜索。
        当前实现只是返回最近的一些文档。
        
        Args:
            limit (int): 返回结果的最大数量
            
        Returns:
            list: 模拟的搜索结果列表
        """
        # 在实际应用中，这里应该实现基于向量相似度的搜索
        # 现在我们只是简单地返回最近的一些文档
        recent_docs = self.local_data[-limit:] if self.local_data else []
        
        # 创建模拟的结果对象
        class MockResult:
            def __init__(self, doc):
                self.entity = MockEntity(doc)
        
        class MockEntity:
            def __init__(self, doc):
                self.doc = doc
                
            def get(self, field_name):
                return self.doc.get(field_name)
        
        return [MockResult(doc) for doc in recent_docs]

    def close(self):
        """
        关闭连接
        
        清理资源，关闭与Milvus数据库的连接。
        """
        if self.use_milvus:
            try:
                from pymilvus import connections
                connections.disconnect("default")
            except:
                pass
        # 本地数据已经在每次操作后自动保存
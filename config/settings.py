"""
配置模块，用于加载和管理应用程序的各种设置参数。
该模块使用dotenv库从.env文件中加载环境变量，并提供默认值以防环境变量未设置。
"""

import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
# 这样可以避免将敏感信息（如API密钥、数据库密码等）硬编码在代码中
load_dotenv()

# OpenAI API密钥配置
# 用于访问OpenAI的GPT模型和其他AI服务
# 如果环境变量中没有设置，则使用占位符值（实际使用时需要替换为真实密钥）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")

# Milvus向量数据库配置
# Milvus是一个开源的向量数据库，专门用于存储和检索高维向量数据
# 常用于AI应用中存储文本嵌入(embeddings)以便进行相似性搜索
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")  # Milvus服务器主机地址
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")     # Milvus服务器端口

# PostgreSQL关系数据库配置
# PostgreSQL是一个强大的开源关系数据库管理系统
# 在本应用中主要用于存储结构化的研究结果和元数据
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")       # PostgreSQL服务器主机地址
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")            # PostgreSQL服务器端口
POSTGRES_USER = os.getenv("POSTGRES_USER", "researcher")      # PostgreSQL用户名
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")  # PostgreSQL密码（空密码）
POSTGRES_DB = os.getenv("POSTGRES_DB", "research_assistant")       # PostgreSQL数据库名

# AI模型配置
# 指定使用的AI模型类型
EMBEDDING_MODEL = "BAAI/bge-large-zh-v1.5"  # 硅基流动的文本嵌入模型，用于将文本转换为向量表示
LLM_MODEL = "Qwen/Qwen2-7B-Instruct"        # 硅基流动的大语言模型，用于生成文本内容

# 功能开关配置
# 控制是否启用Milvus向量数据库功能
USE_MILVUS = os.getenv("USE_MILVUS", "false").lower() == "true"

# 条件配置覆盖
# 如果环境变量中提供了真实的数据库凭据，则更新PostgreSQL配置
# 这是一种安全措施，确保只有在明确设置了凭据的情况下才使用它们
if os.getenv("POSTGRES_USER") and os.getenv("POSTGRES_PASSWORD") is not None:
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    if os.getenv("POSTGRES_DB"):
        POSTGRES_DB = os.getenv("POSTGRES_DB")

# 硅基流动(SiliconFlow) API配置
# 如果使用硅基流动的API，需要设置相应的base_url
SILICONFLOW_API_BASE = "https://api.siliconflow.cn/v1"
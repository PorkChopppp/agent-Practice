"""
研究人员代理模块

研究人员代理（Research Agent）是AI研究助手的核心组件之一，
负责处理用户指定的研究主题，生成相关内容，并将其存储到向量数据库中。

该代理使用自然语言处理技术将文本分割成合适的块，
并利用嵌入模型将文本转换为向量表示以便后续检索。
"""

# 条件导入，避免在没有API密钥时出现问题
# 这种导入方式确保即使缺少某些依赖项，程序也能部分运行
try:
    from langchain_openai import OpenAIEmbeddings
    from openai import OpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from langchain_text_splitters import RecursiveCharacterTextSplitter
from database.milvus_client import MilvusClient
import time
from config.settings import SILICONFLOW_API_BASE

class ResearchAgent:
    """
    研究人员代理类
    
    负责处理研究主题，生成相关内容，并将其存储到向量数据库中。
    使用文本分割器将长文本分解为更小的片段，然后为每个片段生成向量嵌入。
    """
    
    def __init__(self, openai_api_key):
        """
        初始化研究人员代理
        
        Args:
            openai_api_key (str): OpenAI API密钥，用于访问嵌入模型
        """
        # 检查是否可以使用嵌入功能
        # 只有当langchain库可用且API密钥不是默认值时才启用嵌入功能
        self.use_embeddings = LANGCHAIN_AVAILABLE and openai_api_key != "your-api-key-here"
        if self.use_embeddings:
            try:
                # 初始化OpenAI嵌入模型（针对硅基流动API进行配置）
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=openai_api_key,
                    base_url=SILICONFLOW_API_BASE,  # 使用硅基流动的API端点
                    tiktoken_enabled=False,  # 禁用tiktoken以避免连接问题
                    model="BAAI/bge-large-zh-v1.5"  # 指定使用的模型
                )
            except Exception as e:
                # 嵌入模型初始化失败时的错误处理
                print(f"初始化OpenAI嵌入模型失败: {e}")
                self.use_embeddings = False
                self.embeddings = None
        else:
            self.embeddings = None
            
        # 初始化Milvus客户端
        # 使用配置文件中的设置决定是否启用Milvus数据库
        from config.settings import USE_MILVUS
        self.milvus_client = MilvusClient(use_milvus=USE_MILVUS)
        
        # 初始化文本分割器
        # 将长文本分割为适当大小的块，便于处理和存储
        # chunk_size: 每个文本块的最大字符数
        # chunk_overlap: 相邻文本块之间的重叠字符数，确保上下文连续性
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def process_research_topic(self, topic):
        """
        处理研究主题，生成模拟的研究内容并存储到向量数据库
        
        这是研究人员代理的主要功能方法，负责完整的处理流程：
        1. 生成研究内容
        2. 分割文本
        3. 为每个文本片段生成向量嵌入
        4. 存储到向量数据库
        
        在实际应用中，这里会连接到真实的搜索引擎或数据库获取真实数据，
        而不是生成模拟内容。
        
        Args:
            topic (str): 研究主题
            
        Returns:
            str: 处理结果描述
        """
        # 生成示例研究内容
        research_content = self._generate_sample_content(topic)
        
        # 使用文本分割器将内容分割为多个较小的文本片段
        # 这样做是为了更好地适应向量数据库的存储和检索需求
        texts = self.text_splitter.split_text(research_content)
        
        # 为每个文本片段生成嵌入并向量数据库中存储
        for i, text in enumerate(texts):
            # 只有当启用嵌入模型时才生成真实嵌入
            if self.use_embeddings and self.embeddings:
                try:
                    # 使用OpenAI嵌入模型为文本生成向量表示
                    # 嵌入向量捕捉了文本的语义信息，便于后续相似性搜索
                    embedding = self.embeddings.embed_query(text)
                except Exception as e:
                    # 嵌入生成失败时的错误处理
                    print(f"生成嵌入时出错: {e}")
                    # 使用适当维度的模拟嵌入（硅基流动的bge模型是1024维）
                    embedding = [0.0] * 1024
            else:
                # 当嵌入功能不可用时，使用模拟嵌入数据
                # 这确保了即使没有API密钥，系统也能正常运行
                embedding = [0.0] * 1024  # 硅基流动的bge模型是1024维
                
            # 将文本片段及其嵌入存储到Milvus向量数据库中
            self.milvus_client.insert_document(
                content=text,               # 文本内容
                embedding=embedding,        # 文本的向量表示
                source=f"Research on {topic}",  # 数据来源
                timestamp=int(time.time())  # 时间戳
            )
        
        # 返回处理结果信息
        return f"已完成对'{topic}'的研究，共处理了{len(texts)}个文档段落。"

    def _generate_sample_content(self, topic):
        """
        生成示例研究内容
        
        这是一个辅助方法，用于在没有真实数据源的情况下生成示例内容。
        在实际应用中，这部分会被真实的网络爬虫或数据库查询所替代。
        
        Args:
            topic (str): 研究主题
            
        Returns:
            str: 生成的研究内容
        """
        # 预定义的研究内容模板
        # 为常见研究主题提供高质量的示例内容
        content_templates = {
            "人工智能": """
            人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的机器。
            人工智能的历史可以追溯到20世纪50年代，当时艾伦·图灵提出了著名的图灵测试。
            现代AI技术包括机器学习、深度学习、自然语言处理等子领域。
            人工智能的应用非常广泛，涵盖了医疗诊断、金融分析、自动驾驶汽车等多个行业。
            随着计算能力的提升和大数据的普及，人工智能技术得到了快速发展。
            """,
            "机器学习": """
            机器学习是人工智能的一个重要分支，它使计算机能够在不被明确编程的情况下从数据中学习。
            监督学习、无监督学习和强化学习是机器学习的三种主要类型。
            深度学习是一种特殊的机器学习方法，使用多层神经网络来模拟人脑的学习过程。
            机器学习算法在图像识别、语音识别、推荐系统等领域取得了显著成果。
            数据质量和特征工程对于机器学习模型的性能至关重要。
            """,
            "深度学习": """
            深度学习是机器学习的一个子集，基于人工神经网络，特别是深层神经网络。
            卷积神经网络（CNN）在图像处理方面表现出色，而循环神经网络（RNN）适合序列数据处理。
            近年来，Transformer架构在自然语言处理任务中取得了突破性进展。
            深度学习需要大量标注数据和强大的计算资源，如GPU或TPU。
            迁移学习使得在小数据集上训练深度学习模型成为可能。
            """
        }
        
        # 如果主题匹配预定义模板，则返回相应内容，否则返回通用内容
        # 这提高了特定主题内容的质量，同时保持了对任意主题的支持
        return content_templates.get(topic, f"""
        关于{topic}的研究摘要：
        这是一个关于{topic}的重要研究领域。
        该领域包含多个方面和应用场景。
        随着技术的发展，{topic}正变得越来越重要。
        未来，{topic}可能会有更多的创新和发展。
        """)

    def close(self):
        """
        关闭代理连接
        
        清理资源，关闭与Milvus数据库的连接。
        """
        self.milvus_client.close()
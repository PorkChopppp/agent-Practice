"""
写作代理模块

写作代理（Writer Agent）是AI研究助手的另一个核心组件，
负责根据研究人员代理收集的信息编写结构化的研究报告。

该代理使用大型语言模型（LLM）来理解和整合相关信息，
生成专业、连贯的研究报告，并将其保存到关系数据库中。
"""

# 条件导入，避免在没有API密钥时出现问题
# 这种导入方式确保即使缺少某些依赖项，程序也能部分运行
try:
    from langchain_openai import ChatOpenAI
    from langchain_openai import OpenAIEmbeddings
    from openai import OpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from database.milvus_client import MilvusClient
from database.postgres_client import PostgresClient
from config.settings import SILICONFLOW_API_BASE

class WriterAgent:
    """
    写作代理类
    
    负责根据研究主题和相关文档内容编写结构化的研究报告。
    使用大型语言模型来生成自然、连贯的文本内容。
    """
    
    def __init__(self, openai_api_key):
        """
        初始化写作代理
        
        Args:
            openai_api_key (str): OpenAI API密钥，用于访问语言模型和嵌入模型
        """
        # 检查是否可以使用大型语言模型（LLM）
        # 只有当langchain库可用且API密钥不是默认值时才启用LLM功能
        self.use_llm = LANGCHAIN_AVAILABLE and openai_api_key != "your-api-key-here"
        if self.use_llm:
            try:
                # 初始化ChatOpenAI语言模型（针对硅基流动API进行配置）
                # model_name: 使用的模型名称（这里是Qwen2-7B-Instruct）
                # temperature: 控制生成文本的随机性，0.7是一个适中的值
                self.llm = ChatOpenAI(
                    openai_api_key=openai_api_key,
                    model_name="Qwen/Qwen2-7B-Instruct",
                    base_url=SILICONFLOW_API_BASE,  # 使用硅基流动的API端点
                    temperature=0.7
                )
            except Exception as e:
                # LLM初始化失败时的错误处理
                print(f"初始化ChatOpenAI失败: {e}")
                self.use_llm = False
                self.llm = None
        else:
            # 当无法使用LLM时的通知信息
            print("未提供有效的OpenAI API密钥或缺少依赖，将使用模拟响应")
            self.llm = None
        
        # 检查是否可以使用嵌入功能
        self.use_embeddings = LANGCHAIN_AVAILABLE and openai_api_key != "your-api-key-here"
        if self.use_embeddings:
            try:
                # 初始化OpenAI嵌入模型，用于生成查询向量（针对硅基流动API进行配置）
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
            
        # 初始化数据库客户端
        # Milvus客户端用于检索相关文档内容
        # 不再默认禁用Milvus，而是根据配置决定是否启用
        from config.settings import USE_MILVUS
        print(f"写作代理Milvus功能开关: {USE_MILVUS}")
        self.milvus_client = MilvusClient(use_milvus=USE_MILVUS)
        # PostgreSQL客户端用于保存生成的研究报告
        self.postgres_client = PostgresClient()

    def write_report(self, topic):
        """
        根据研究主题编写报告
        
        这是写作代理的主要功能方法，负责完整的报告生成流程：
        1. 生成查询向量
        2. 从向量数据库中检索相关信息
        3. 使用LLM生成报告
        4. 保存报告到关系数据库
        
        Args:
            topic (str): 研究主题
            
        Returns:
            dict: 包含报告ID、主题和内容的字典
        """
        try:
            # 生成查询向量，用于在向量数据库中搜索相关内容
            if self.use_embeddings and self.embeddings:
                # 使用嵌入模型为研究主题生成向量表示
                query_embedding = self.embeddings.embed_query(topic)
                
                # 从向量数据库中检索与主题最相关的文档
                # limit=5 表示最多检索5个相关文档
                similar_docs = self.milvus_client.search_similar_documents(query_embedding, limit=5)
                
                # 提取检索到的文档内容
                doc_contents = [doc.entity.get('content') for doc in similar_docs]
            else:
                # 当嵌入功能不可用时抛出异常，触发错误处理流程
                raise Exception("未初始化嵌入模型")
        except Exception as e:
            # 错误处理：当检索文档失败时使用默认内容继续
            print(f"从Milvus检索文档时出错: {e}")
            print("使用默认内容继续...")
            # 使用默认内容作为文档内容，确保流程可以继续执行
            doc_contents = [f"这是关于{topic}的默认内容。在实际应用中，这将是从向量数据库中检索到的相关文档内容。"]
        
        # 使用LLM根据文档内容生成研究报告
        report_content = self._generate_report_from_docs(topic, doc_contents)
        
        # 将生成的报告保存到PostgreSQL关系数据库中
        report_id = self.postgres_client.save_report(topic, report_content)
        
        # 返回报告信息
        return {
            "report_id": report_id,    # 报告ID
            "topic": topic,            # 报告主题
            "content": report_content  # 报告内容
        }

    def _generate_report_from_docs(self, topic, doc_contents):
        """
        根据文档内容生成报告
        
        使用大型语言模型整合多个文档内容，生成结构化的研究报告。
        如果无法使用LLM，则返回预先编写的模拟内容。
        
        Args:
            topic (str): 研究主题
            doc_contents (list): 相关文档内容列表
            
        Returns:
            str: 生成的研究报告内容
        """
        # 将多个文档内容合并为一个字符串，每个文档之间用两个换行符分隔
        docs_text = "\n\n".join([f"文档 {i+1}: {content}" for i, content in enumerate(doc_contents)])
        
        # 检查是否可以使用LLM
        if self.use_llm and self.llm:
            # 构造提示词（Prompt），指导LLM如何生成报告
            prompt = f"""
            基于以下关于"{topic}"的文档内容，撰写一份结构化的研究报告：

            {docs_text}

            要求：
            1. 报告应包含引言、主要内容和结论
            2. 使用清晰、专业的语言
            3. 整合所有文档中的关键信息
            4. 报告长度约300-500字
            
            研究报告:
            """
            
            # 调用LLM生成报告
            try:
                # 使用invoke方法调用语言模型
                response = self.llm.invoke(prompt)
                # 返回生成的报告内容
                return response.content
            except Exception as e:
                # LLM调用失败时的错误处理
                print(f"调用LLM时出错: {e}")
                print("使用模拟报告内容...")
        
        # 当没有使用LLM或出现错误时，返回预先编写的模拟内容
        # 这确保了即使没有API密钥或网络连接，系统也能生成基本的报告内容
        return f"""
# {topic}研究报告

## 引言

{topic}是当前科技领域的热门话题。本报告旨在探讨其基本概念、应用领域及未来发展趋势。

## 主要内容

根据收集到的资料，{topic}具有以下几个关键特点：
1. 技术先进性：采用了最新的算法和技术
2. 应用广泛性：在多个行业中都有实际应用
3. 发展潜力大：未来仍有很大的发展空间

相关文档提到了以下要点：
{chr(10).join([f"- {content[:100]}..." for content in doc_contents])}

## 结论

{topic}作为一个重要的技术领域，其价值和意义不言而喻。随着技术的不断发展和完善，预计在未来几年内会有更多的突破和创新。

---
*本报告由AI自动生成*
"""

    def close(self):
        """
        关闭代理连接
        
        清理资源，关闭与各个数据库的连接。
        """
        try:
            self.milvus_client.close()
        except:
            pass
        self.postgres_client.close()
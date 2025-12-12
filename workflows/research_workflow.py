"""
研究工作流模块

研究工作流（Research Workflow）负责协调研究人员代理和写作代理，
形成一个完整的AI研究助手工作流。

该模块定义了从研究主题处理到报告生成的完整自动化流程，
同时展示了如何使用LangGraph构建更复杂的工作流。
"""

from agents.researcher_agent import ResearchAgent
from agents.writer_agent import WriterAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.review_agent import ReviewAgent
from config.settings import OPENAI_API_KEY

class ResearchWorkflow:
    """
    研究工作流类
    
    负责协调研究人员代理和写作代理，执行完整的研究流程。
    包括主题研究、信息收集、报告生成和保存等步骤。
    """
    
    def __init__(self):
        """
        初始化研究工作流
        
        创建研究人员代理和写作代理实例，准备执行研究任务。
        """
        # 初始化研究人员代理，负责处理研究主题和收集信息
        self.research_agent = ResearchAgent(OPENAI_API_KEY)
        # 初始化写作代理，负责生成研究报告
        self.writer_agent = WriterAgent(OPENAI_API_KEY)
        # 初始化知识管理代理，负责知识库管理
        self.knowledge_agent = KnowledgeAgent()
        # 初始化评审代理，负责内容质量评估
        self.review_agent = ReviewAgent()
        
    def run_research_process(self, topic):
        """
        运行完整的研究流程
        
        按顺序执行研究和写作两个阶段，完成从主题到报告的全过程。
        
        Args:
            topic (str): 研究主题
            
        Returns:
            dict: 生成的研究报告信息
        """
        print(f"开始研究主题: {topic}")
        
        # 步骤1: 研究代理处理主题
        # 研究人员代理负责收集与主题相关的信息并存储到向量数据库
        research_result = self.research_agent.process_research_topic(topic)
        print(research_result)
        
        # 步骤2: 写作代理生成报告
        # 写作代理从向量数据库中检索相关信息，并生成结构化的研究报告
        print("正在生成研究报告...")
        report = self.writer_agent.write_report(topic)
        
        # 步骤3: 评审代理评估报告质量
        print("正在评估报告质量...")
        review_result = self.review_agent.review_report(report["content"], topic)
        report["review"] = review_result
        
        # 步骤4: 将报告添加到知识库
        print("正在将报告添加到知识库...")
        knowledge_metadata = {
            "source": f"Research on {topic}",
            "type": "research_report",
            "topic": topic
        }
        self.knowledge_agent.add_knowledge(report["content"], knowledge_metadata)
        
        print(f"研究报告已生成并保存，ID: {report['report_id']}")
        return report

    def close(self):
        """
        关闭所有连接
        
        清理资源，关闭所有代理的数据库连接。
        """
        self.research_agent.close()
        self.writer_agent.close()
        self.knowledge_agent.close()

# 使用LangGraph构建更复杂的工作流（可选）
def create_graph_workflow():
    """
    创建基于LangGraph的工作流
    
    LangGraph是一个用于构建复杂代理工作流的框架，
    允许定义状态、节点和边来控制执行流程。
    
    这个函数演示了如何使用LangGraph创建更灵活的工作流结构。
    """
    # 初始化代理
    research_agent = ResearchAgent(OPENAI_API_KEY)
    writer_agent = WriterAgent(OPENAI_API_KEY)
    knowledge_agent = KnowledgeAgent()
    review_agent = ReviewAgent()
    
    # 定义工作流节点函数
    # 每个节点函数接收当前状态作为输入，返回更新后的状态
    
    def research_node(state):
        """
        研究节点函数
        
        Args:
            state (dict): 当前工作流状态
            
        Returns:
            dict: 更新后的状态，包含研究结果
        """
        topic = state["topic"]
        result = research_agent.process_research_topic(topic)
        return {"research_result": result}
    
    def write_node(state):
        """
        写作节点函数
        
        Args:
            state (dict): 当前工作流状态
            
        Returns:
            dict: 更新后的状态，包含生成的报告
        """
        topic = state["topic"]
        report = writer_agent.write_report(topic)
        return {"report": report}
    
    def review_node(state):
        """
        评审节点函数
        
        Args:
            state (dict): 当前工作流状态
            
        Returns:
            dict: 更新后的状态，包含评审结果
        """
        report = state["report"]
        review_result = review_agent.review_report(report["content"], report.get("topic", ""))
        report["review"] = review_result
        return {"report": report}
    
    def knowledge_node(state):
        """
        知识管理节点函数
        
        Args:
            state (dict): 当前工作流状态
            
        Returns:
            dict: 更新后的状态
        """
        report = state["report"]
        knowledge_metadata = {
            "source": f"Research Report ID: {report['report_id']}",
            "type": "research_report",
            "topic": report.get("topic", "")
        }
        knowledge_agent.add_knowledge(report["content"], knowledge_metadata)
        return {"knowledge_added": True}
    
    # 注意：在新版本的langgraph中，应该使用StateGraph而不是Graph
    # StateGraph提供了更好的状态管理和节点间通信机制
    from langgraph.graph import StateGraph
    
    # 创建图工作流对象
    # 使用字典作为状态对象，可以在节点间传递数据
    workflow = StateGraph(dict)
    
    # 添加节点到工作流
    # 每个节点代表一个处理步骤
    workflow.add_node("research", research_node)    # 研究节点
    workflow.add_node("write", write_node)          # 写作节点
    workflow.add_node("review", review_node)        # 评审节点
    workflow.add_node("knowledge", knowledge_node)  # 知识管理节点
    
    # 添加边定义节点执行顺序
    workflow.add_edge("research", "write")
    workflow.add_edge("write", "review")
    workflow.add_edge("review", "knowledge")
    
    # 设置入口和出口点
    # 入口点是工作流开始执行的第一个节点
    workflow.set_entry_point("research")
    # 出口点是工作流结束的最后一个节点
    workflow.set_finish_point("knowledge")
    
    # 编译工作流为可执行对象
    return workflow.compile()
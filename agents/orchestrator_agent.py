"""
协调者代理模块

协调者代理（Orchestrator Agent）负责协调多个代理的工作，
管理整个研究流程的执行顺序和决策逻辑。
"""

from typing import Dict, List, Any
from agents.researcher_agent import ResearchAgent
from agents.writer_agent import WriterAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.review_agent import ReviewAgent
from config.settings import OPENAI_API_KEY

class OrchestratorAgent:
    """
    协调者代理类
    
    负责协调多个代理的工作，管理整个研究流程的执行。
    """
    
    def __init__(self):
        """
        初始化协调者代理
        """
        self.research_agent = ResearchAgent(OPENAI_API_KEY)
        self.writer_agent = WriterAgent(OPENAI_API_KEY)
        self.knowledge_agent = KnowledgeAgent()
        self.review_agent = ReviewAgent()
        print("协调者代理初始化完成")
    
    def execute_research_task(self, topic: str, depth: str = "basic") -> Dict[str, Any]:
        """
        执行研究任务
        
        Args:
            topic (str): 研究主题
            depth (str): 研究深度（basic, intermediate, deep）
            
        Returns:
            dict: 研究结果
        """
        print(f"协调者代理开始执行研究任务: {topic}")
        
        # 根据研究深度调整参数
        if depth == "deep":
            # 深度研究：多次迭代，更详细的内容
            iterations = 3
        elif depth == "intermediate":
            # 中等研究：两次迭代
            iterations = 2
        else:
            # 基础研究：单次执行
            iterations = 1
        
        final_result = None
        
        for i in range(iterations):
            print(f"执行第 {i+1} 轮研究...")
            
            # 第一步：研究代理处理主题
            research_result = self.research_agent.process_research_topic(f"{topic} (第{i+1}轮)")
            print(research_result)
            
            # 第二步：写作代理生成报告
            report = self.writer_agent.write_report(topic)
            
            # 第三步：评审代理评估报告
            review_result = self.review_agent.review_report(report["content"], topic)
            report["review"] = review_result
            
            # 保存中间结果
            final_result = report
        
        # 第四步：将最终报告添加到知识库
        if final_result:
            knowledge_metadata = {
                "source": f"Research on {topic}",
                "type": "research_report",
                "topic": topic,
                "depth": depth
            }
            self.knowledge_agent.add_knowledge(final_result["content"], knowledge_metadata)
            
            # 获取知识库统计信息
            stats = self.knowledge_agent.get_knowledge_stats()
            final_result["knowledge_stats"] = stats
        
        print("研究任务执行完成")
        return final_result if final_result else {}
    
    def query_knowledge_base(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        查询知识库
        
        Args:
            query (str): 查询内容
            limit (int): 返回结果数量限制
            
        Returns:
            list: 查询结果
        """
        print(f"查询知识库: {query}")
        return self.knowledge_agent.search_knowledge(query, limit)
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        获取系统状态
        
        Returns:
            dict: 系统状态信息
        """
        stats = self.knowledge_agent.get_knowledge_stats()
        return {
            "status": "running",
            "agents": ["research_agent", "writer_agent", "knowledge_agent", "review_agent"],
            "knowledge_base_stats": stats,
            "timestamp": "2025-12-12"
        }
    
    def close(self):
        """
        关闭所有代理连接
        """
        try:
            self.research_agent.close()
        except:
            pass
        try:
            self.writer_agent.close()
        except:
            pass
        try:
            self.knowledge_agent.close()
        except:
            pass
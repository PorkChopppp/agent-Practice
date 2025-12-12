"""
AI研究助手主程序

这是AI研究助手应用程序的入口点，负责初始化工作流、
处理命令行参数、执行研究流程并显示结果。

该程序演示了如何将研究人员代理和写作代理组合成一个
完整的工作流程，实现从研究主题到研究报告的自动化生成。
"""

from workflows.research_workflow import ResearchWorkflow, create_graph_workflow
from agents.orchestrator_agent import OrchestratorAgent
import sys
import argparse

def main():
    """
    主函数
    
    程序的入口点，负责整个执行流程：
    1. 初始化研究工作流
    2. 获取研究主题（从命令行参数或默认值）
    3. 执行研究流程
    4. 显示生成的报告
    5. 清理资源
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="AI研究助手")
    parser.add_argument("topic", nargs="?", default="人工智能", help="研究主题")
    parser.add_argument("--mode", choices=["simple", "workflow", "orchestrator"], 
                       default="simple", help="执行模式")
    parser.add_argument("--depth", choices=["basic", "intermediate", "deep"], 
                       default="basic", help="研究深度")
    
    args = parser.parse_args()
    topic = args.topic
    
    try:
        if args.mode == "workflow":
            # 使用LangGraph工作流模式
            print("使用LangGraph工作流模式...")
            workflow = create_graph_workflow()
            result = workflow.invoke({"topic": topic})
            print("工作流执行完成")
        elif args.mode == "orchestrator":
            # 使用协调者代理模式
            print("使用协调者代理模式...")
            orchestrator = OrchestratorAgent()
            result = orchestrator.execute_research_task(topic, args.depth)
            orchestrator.close()
        else:
            # 使用简单模式
            print("使用简单模式...")
            # 创建研究工作流实例
            workflow = ResearchWorkflow()
            
            # 运行研究流程
            # 这将依次执行研究和写作两个阶段
            result = workflow.run_research_process(topic)
            
            # 关闭所有连接，确保资源得到正确释放
            workflow.close()
        
        # 显示生成的研究报告
        # 使用格式化输出使报告更易读
        print("\n" + "="*50)
        print("生成的研究报告:")
        print("="*50)
        
        if isinstance(result, dict):
            print(f"主题: {result.get('topic', topic)}")      # 显示报告主题
            print(f"报告ID: {result.get('report_id', 'N/A')}")  # 显示报告ID
            print("-"*50)
            print(result.get('content', '无内容'))
            
            # 显示评审结果
            if 'review' in result:
                review = result['review']
                print("\n" + "-"*30)
                print("报告评审结果:")
                print("-"*30)
                print(f"质量评分: {review.get('quality_score', 'N/A')}/100")
                print(f"综合评估: {review.get('overall_assessment', 'N/A')}")
                if review.get('feedback'):
                    print("反馈意见:")
                    for feedback in review['feedback']:
                        print(f"  - {feedback}")
                if review.get('suggestions'):
                    print("改进建议:")
                    for suggestion in review['suggestions']:
                        print(f"  - {suggestion}")
            
            # 显示知识库统计
            if 'knowledge_stats' in result:
                stats = result['knowledge_stats']
                print("\n" + "-"*30)
                print("知识库统计:")
                print("-"*30)
                print(f"总知识条目: {stats.get('total_knowledge', 'N/A')}")
                print(f"数据来源: {', '.join(stats.get('sources', []))}")
        else:
            print(result)
            
        print("="*50)
        
    except Exception as e:
        # 执行过程中出现错误时的处理
        print(f"执行过程中出现错误: {e}")
        print("这可能是由于缺少必要的API密钥或数据库连接导致的")
    finally:
        # 关闭所有连接，确保资源得到正确释放
        try:
            if 'workflow' in locals():
                workflow.close()
        except:
            pass

# 程序入口点
# 只有当脚本被直接运行时（而不是被导入时）才会执行main函数
if __name__ == "__main__":
    main()
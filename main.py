"""
AI研究助手主程序

这是AI研究助手应用程序的入口点，负责初始化工作流、
处理命令行参数、执行研究流程并显示结果。

该程序演示了如何将研究人员代理和写作代理组合成一个
完整的工作流程，实现从研究主题到研究报告的自动化生成。
"""

from workflows.research_workflow import ResearchWorkflow
import sys

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
    # 创建研究工作流实例
    try:
        # 初始化研究工作流，包括研究人员代理和写作代理
        workflow = ResearchWorkflow()
    except Exception as e:
        # 工作流初始化失败时的错误处理
        print(f"无法初始化工作流: {e}")
        print("请检查配置和依赖项是否正确安装")
        return
    
    # 获取研究主题
    # 支持从命令行参数传入研究主题，如果没有提供则使用默认主题
    if len(sys.argv) > 1:
        # 如果提供了命令行参数，则将其作为研究主题
        topic = " ".join(sys.argv[1:])
    else:
        # 如果没有提供命令行参数，则使用默认主题"人工智能"
        topic = "人工智能"
    
    try:
        # 运行研究流程
        # 这将依次执行研究和写作两个阶段
        report = workflow.run_research_process(topic)
        
        # 显示生成的研究报告
        # 使用格式化输出使报告更易读
        print("\n" + "="*50)
        print("生成的研究报告:")
        print("="*50)
        print(f"主题: {report['topic']}")      # 显示报告主题
        print(f"报告ID: {report['report_id']}")  # 显示报告ID
        print("-"*50)
        print(report['content'])              # 显示报告内容
        print("="*50)
        
    except Exception as e:
        # 执行过程中出现错误时的处理
        print(f"执行过程中出现错误: {e}")
        print("这可能是由于缺少必要的API密钥或数据库连接导致的")
    finally:
        # 关闭所有连接，确保资源得到正确释放
        try:
            workflow.close()
        except:
            pass

# 程序入口点
# 只有当脚本被直接运行时（而不是被导入时）才会执行main函数
if __name__ == "__main__":
    main()
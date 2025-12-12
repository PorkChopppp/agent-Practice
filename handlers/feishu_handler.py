"""
飞书消息处理器

处理来自飞书的消息和事件，调用相应的办公助理功能。
"""

import json
from typing import Dict, Any
from agents.office_assistant_agent import OfficeAssistantAgent
from integrations.feishu_integration import FeishuIntegration
from config.settings import OPENAI_API_KEY
import os


class FeishuHandler:
    """
    飞书消息处理器
    
    负责接收和处理来自飞书的消息和事件，调用办公助理代理执行相应操作。
    """
    
    def __init__(self):
        """
        初始化飞书消息处理器
        """
        # 初始化办公助理代理
        self.office_agent = OfficeAssistantAgent()
        
        # 初始化飞书集成
        self.feishu = FeishuIntegration(
            app_id=os.getenv("FEISHU_APP_ID"),
            app_secret=os.getenv("FEISHU_APP_SECRET"),
            webhook_url=os.getenv("FEISHU_WEBHOOK_URL")
        )
        
        print("飞书消息处理器初始化完成")
    
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理飞书消息
        
        Args:
            message (dict): 消息内容
            
        Returns:
            dict: 处理结果
        """
        try:
            # 解析命令
            parsed = self.feishu.parse_command(message)
            command = parsed["command"]
            args = parsed["args"]
            
            # 根据命令执行相应操作
            if command == "help":
                return self._handle_help()
            elif command == "创建任务":
                return self._handle_create_task(args)
            elif command == "我的任务":
                return self._handle_my_tasks(args)
            elif command == "任务状态":
                return self._handle_update_task_status(args)
            elif command == "安排会议":
                return self._handle_schedule_meeting(args)
            elif command == "近期事件":
                return self._handle_upcoming_events(args)
            elif command == "搜索":
                return self._handle_search(args)
            elif command == "统计":
                return self._handle_statistics()
            else:
                return self._handle_unknown_command(command)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"处理消息时出错: {e}"
            }
    
    def _handle_help(self) -> Dict[str, Any]:
        """
        处理帮助命令
        
        Returns:
            dict: 响应内容
        """
        help_text = (
            "我是您的办公助理，可以帮助您处理日常办公事务。\n\n"
            "支持的命令：\n"
            "📌 创建任务 <标题> [负责人] [优先级1-3] [截止日期YYYY-MM-DD] - 创建新任务\n"
            "📌 我的任务 [状态] - 查看分配给我的任务\n"
            "📌 任务状态 <任务ID> <状态> - 更新任务状态(pending/in_progress/completed)\n"
            "📌 安排会议 <标题> <开始时间> <结束时间> <参会人1,参会人2> [地点] - 安排会议\n"
            "📌 近期事件 [天数] - 查看近期的会议和任务\n"
            "📌 搜索 <关键词> - 搜索任务和会议\n"
            "📌 统计 - 查看办公统计数据\n"
            "📌 help - 显示帮助信息"
        )
        
        return {
            "success": True,
            "message": help_text
        }
    
    def _handle_create_task(self, args: str) -> Dict[str, Any]:
        """
        处理创建任务命令
        
        Args:
            args (str): 命令参数
            
        Returns:
            dict: 处理结果
        """
        if not args:
            return {
                "success": False,
                "message": "请提供任务标题，格式：创建任务 <标题> [负责人] [优先级1-3] [截止日期YYYY-MM-DD]"
            }
        
        # 解析参数
        parts = args.split()
        title = parts[0] if len(parts) > 0 else ""
        assignee = parts[1] if len(parts) > 1 else ""
        priority = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 1
        due_date = parts[3] if len(parts) > 3 else None
        
        if not title:
            return {
                "success": False,
                "message": "请提供任务标题"
            }
        
        # 创建任务
        result = self.office_agent.create_task(title, "", assignee, priority, due_date)
        return result
    
    def _handle_my_tasks(self, args: str) -> Dict[str, Any]:
        """
        处理我的任务命令
        
        Args:
            args (str): 命令参数
            
        Returns:
            dict: 处理结果
        """
        # 这里应该从消息中获取用户信息，暂时使用默认值
        assignee = ""  # 实际应用中应该从消息中提取用户标识
        status = args.strip() if args else None
        
        tasks = self.office_agent.get_tasks(assignee=assignee, status=status)
        
        if not tasks:
            return {
                "success": True,
                "message": "暂无符合条件的任务"
            }
        
        # 格式化任务列表
        message = f"找到 {len(tasks)} 个任务：\n"
        for task in tasks:
            message += f"\n📌 [{task['id']}] {task['title']}\n"
            message += f"   状态: {task['status']} | 优先级: {task['priority']}\n"
            if task['assignee']:
                message += f"   负责人: {task['assignee']}\n"
            if task['due_date']:
                message += f"   截止日期: {task['due_date'][:10]}\n"
        
        return {
            "success": True,
            "message": message
        }
    
    def _handle_update_task_status(self, args: str) -> Dict[str, Any]:
        """
        处理更新任务状态命令
        
        Args:
            args (str): 命令参数
            
        Returns:
            dict: 处理结果
        """
        parts = args.split()
        if len(parts) < 2:
            return {
                "success": False,
                "message": "参数不足，格式：任务状态 <任务ID> <状态>"
            }
        
        try:
            task_id = int(parts[0])
            status = parts[1].lower()
            
            if status not in ["pending", "in_progress", "completed"]:
                return {
                    "success": False,
                    "message": "状态必须是以下之一: pending, in_progress, completed"
                }
            
            result = self.office_agent.update_task_status(task_id, status)
            return result
        except ValueError:
            return {
                "success": False,
                "message": "任务ID必须是数字"
            }
    
    def _handle_schedule_meeting(self, args: str) -> Dict[str, Any]:
        """
        处理安排会议命令
        
        Args:
            args (str): 命令参数
            
        Returns:
            dict: 处理结果
        """
        # 简化处理，实际应用中需要更复杂的参数解析
        return {
            "success": True,
            "message": "会议安排功能已在开发中，敬请期待！"
        }
    
    def _handle_upcoming_events(self, args: str) -> Dict[str, Any]:
        """
        处理近期事件命令
        
        Args:
            args (str): 命令参数
            
        Returns:
            dict: 处理结果
        """
        try:
            days = int(args) if args.isdigit() else 7
        except ValueError:
            days = 7
        
        events = self.office_agent.get_upcoming_events(days)
        
        if not events:
            return {
                "success": True,
                "message": f"最近 {days} 天内没有安排的事件"
            }
        
        message = f"最近 {days} 天内的事件：\n"
        for event in events:
            if event["type"] == "meeting":
                message += f"\n👥 会议: {event['title']}\n"
                message += f"   时间: {event['start_time'][:16]}\n"
                if event['location']:
                    message += f"   地点: {event['location']}\n"
            else:  # task
                message += f"\n✅ 任务: {event['title']}\n"
                message += f"   截止日期: {event['due_date'][:16]}\n"
                if event['assignee']:
                    message += f"   负责人: {event['assignee']}\n"
        
        return {
            "success": True,
            "message": message
        }
    
    def _handle_search(self, args: str) -> Dict[str, Any]:
        """
        处理搜索命令
        
        Args:
            args (str): 命令参数
            
        Returns:
            dict: 处理结果
        """
        if not args:
            return {
                "success": False,
                "message": "请提供搜索关键词"
            }
        
        result = self.office_agent.search_office_info(args)
        
        if "error" in result:
            return {
                "success": False,
                "message": result["message"]
            }
        
        message = f"搜索 '{args}' 的结果：\n"
        
        if result["total_tasks"] > 0:
            message += f"\n📋 相关任务 ({result['total_tasks']} 个)：\n"
            for task in result["tasks"]:
                message += f"   [{task['id']}] {task['title']}\n"
        
        if result["total_meetings"] > 0:
            message += f"\n👥 相关会议 ({result['total_meetings']} 个)：\n"
            for meeting in result["meetings"]:
                message += f"   [{meeting['id']}] {meeting['title']}\n"
        
        if result["total_tasks"] == 0 and result["total_meetings"] == 0:
            message += "\n未找到相关结果"
        
        return {
            "success": True,
            "message": message
        }
    
    def _handle_statistics(self) -> Dict[str, Any]:
        """
        处理统计命令
        
        Returns:
            dict: 处理结果
        """
        stats = self.office_agent.get_statistics()
        
        if "error" in stats:
            return {
                "success": False,
                "message": stats["message"]
            }
        
        tasks = stats["tasks"]
        message = "📊 办公统计数据：\n\n"
        message += f"📝 任务总数: {tasks['total']}\n"
        message += f"   已完成: {tasks['completed']}\n"
        message += f"   进行中: {tasks['in_progress']}\n"
        message += f"   待处理: {tasks['pending']}\n\n"
        message += f"📅 今日会议: {stats['today_meetings']} 个"
        
        return {
            "success": True,
            "message": message
        }
    
    def _handle_unknown_command(self, command: str) -> Dict[str, Any]:
        """
        处理未知命令
        
        Args:
            command (str): 未知命令
            
        Returns:
            dict: 处理结果
        """
        return {
            "success": False,
            "message": f"未知命令: {command}\n请输入 'help' 查看可用命令"
        }
    
    def close(self):
        """
        关闭处理器连接
        """
        try:
            self.office_agent.close()
        except:
            pass
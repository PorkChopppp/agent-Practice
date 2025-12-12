"""
办公助理代理模块

办公助理代理（Office Assistant Agent）负责处理日常办公任务，
包括日程管理、任务跟踪、信息查询等，并支持通过飞书进行交互。
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from database.postgres_client import PostgresClient


class OfficeAssistantAgent:
    """
    办公助理代理类
    
    负责处理日常办公任务，如日程管理、任务分配、信息查询等，
    并可通过飞书等平台与用户进行交互。
    """
    
    def __init__(self):
        """
        初始化办公助理代理
        """
        self.postgres_client = PostgresClient()
        self._initialize_database()
        print("办公助理代理初始化完成")
    
    def _initialize_database(self):
        """
        初始化数据库表
        """
        try:
            conn = self.postgres_client.get_connection()
            if not conn:
                print("数据库未连接，跳过表初始化")
                return
                
            cursor = conn.cursor()
            
            # 创建任务表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS office_tasks (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    assignee VARCHAR(100),
                    priority INTEGER DEFAULT 1,
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    due_date TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
            
            # 创建日程表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS office_schedule (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    participants TEXT[],
                    location VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            print("办公助理数据库表初始化完成")
        except Exception as e:
            print(f"初始化数据库表时出错: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def create_task(self, title: str, description: str = "", assignee: str = "", 
                   priority: int = 1, due_date: str = None) -> Dict[str, Any]:
        """
        创建新任务
        
        Args:
            title (str): 任务标题
            description (str): 任务描述
            assignee (str): 负责人
            priority (int): 优先级 (1-3)
            due_date (str): 截止日期 (YYYY-MM-DD)
            
        Returns:
            dict: 任务创建结果
        """
        try:
            conn = self.postgres_client.get_connection()
            if not conn:
                return {
                    "success": False,
                    "error": "Database not connected",
                    "message": "数据库未连接，无法创建任务"
                }
                
            cursor = conn.cursor()
            
            # 插入任务
            cursor.execute("""
                INSERT INTO office_tasks (title, description, assignee, priority, due_date)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (title, description, assignee, priority, due_date))
            
            task_id = cursor.fetchone()[0]
            conn.commit()
            
            return {
                "success": True,
                "task_id": task_id,
                "message": f"任务 '{title}' 创建成功"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"创建任务时出错: {e}"
            }
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def get_tasks(self, assignee: str = None, status: str = None) -> List[Dict[str, Any]]:
        """
        获取任务列表
        
        Args:
            assignee (str): 负责人筛选
            status (str): 状态筛选
            
        Returns:
            list: 任务列表
        """
        try:
            conn = self.postgres_client.get_connection()
            if not conn:
                return []
                
            cursor = conn.cursor()
            
            # 构建查询条件
            query = "SELECT id, title, description, assignee, priority, status, created_at, due_date FROM office_tasks WHERE 1=1"
            params = []
            
            if assignee:
                query += " AND assignee = %s"
                params.append(assignee)
                
            if status:
                query += " AND status = %s"
                params.append(status)
            
            query += " ORDER BY priority DESC, created_at ASC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            tasks = []
            for row in rows:
                tasks.append({
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "assignee": row[3],
                    "priority": row[4],
                    "status": row[5],
                    "created_at": row[6].isoformat() if row[6] else None,
                    "due_date": row[7].isoformat() if row[7] else None
                })
            
            return tasks
        except Exception as e:
            print(f"获取任务列表时出错: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def update_task_status(self, task_id: int, status: str) -> Dict[str, Any]:
        """
        更新任务状态
        
        Args:
            task_id (int): 任务ID
            status (str): 新状态 (pending, in_progress, completed)
            
        Returns:
            dict: 更新结果
        """
        try:
            conn = self.postgres_client.get_connection()
            if not conn:
                return {
                    "success": False,
                    "error": "Database not connected",
                    "message": "数据库未连接，无法更新任务状态"
                }
                
            cursor = conn.cursor()
            
            # 更新任务状态
            if status == "completed":
                cursor.execute("""
                    UPDATE office_tasks 
                    SET status = %s, completed_at = CURRENT_TIMESTAMP 
                    WHERE id = %s
                """, (status, task_id))
            else:
                cursor.execute("""
                    UPDATE office_tasks 
                    SET status = %s 
                    WHERE id = %s
                """, (status, task_id))
            
            conn.commit()
            
            if cursor.rowcount > 0:
                return {
                    "success": True,
                    "message": f"任务状态已更新为 '{status}'"
                }
            else:
                return {
                    "success": False,
                    "message": "未找到指定的任务"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"更新任务状态时出错: {e}"
            }
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def schedule_meeting(self, title: str, start_time: str, end_time: str,
                        participants: List[str], location: str = "", 
                        description: str = "") -> Dict[str, Any]:
        """
        安排会议
        
        Args:
            title (str): 会议标题
            start_time (str): 开始时间 (YYYY-MM-DD HH:MM)
            end_time (str): 结束时间 (YYYY-MM-DD HH:MM)
            participants (list): 参会人员列表
            location (str): 会议地点
            description (str): 会议描述
            
        Returns:
            dict: 会议安排结果
        """
        try:
            conn = self.postgres_client.get_connection()
            if not conn:
                return {
                    "success": False,
                    "error": "Database not connected",
                    "message": "数据库未连接，无法安排会议"
                }
                
            cursor = conn.cursor()
            
            # 插入会议安排
            cursor.execute("""
                INSERT INTO office_schedule (title, description, start_time, end_time, participants, location)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (title, description, start_time, end_time, participants, location))
            
            meeting_id = cursor.fetchone()[0]
            conn.commit()
            
            return {
                "success": True,
                "meeting_id": meeting_id,
                "message": f"会议 '{title}' 安排成功"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"安排会议时出错: {e}"
            }
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def get_upcoming_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取即将到来的事件（会议、任务截止等）
        
        Args:
            days (int): 查询天数，默认7天
            
        Returns:
            list: 事件列表
        """
        try:
            conn = self.postgres_client.get_connection()
            if not conn:
                return []
                
            cursor = conn.cursor()
            
            # 查询即将召开的会议
            cursor.execute("""
                SELECT id, title, description, start_time, end_time, participants, location
                FROM office_schedule 
                WHERE start_time BETWEEN NOW() AND NOW() + INTERVAL '%s days'
                ORDER BY start_time ASC
            """, (days,))
            
            meetings = []
            for row in cursor.fetchall():
                meetings.append({
                    "type": "meeting",
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "start_time": row[3].isoformat() if row[3] else None,
                    "end_time": row[4].isoformat() if row[4] else None,
                    "participants": row[5],
                    "location": row[6]
                })
            
            # 查询即将到期的任务
            cursor.execute("""
                SELECT id, title, description, assignee, due_date
                FROM office_tasks 
                WHERE status != 'completed' AND due_date BETWEEN NOW() AND NOW() + INTERVAL '%s days'
                ORDER BY due_date ASC
            """, (days,))
            
            tasks = []
            for row in cursor.fetchall():
                tasks.append({
                    "type": "task",
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "assignee": row[3],
                    "due_date": row[4].isoformat() if row[4] else None
                })
            
            # 合并并按时间排序
            events = meetings + tasks
            events.sort(key=lambda x: x.get("start_time") or x.get("due_date"))
            
            return events
        except Exception as e:
            print(f"获取即将到来的事件时出错: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def search_office_info(self, query: str) -> Dict[str, Any]:
        """
        搜索办公相关信息
        
        Args:
            query (str): 搜索关键词
            
        Returns:
            dict: 搜索结果
        """
        try:
            conn = self.postgres_client.get_connection()
            if not conn:
                return {
                    "error": "Database not connected",
                    "message": "数据库未连接，无法搜索信息",
                    "tasks": [],
                    "meetings": []
                }
                
            cursor = conn.cursor()
            
            # 在任务和会议中搜索
            search_pattern = f"%{query}%"
            
            # 搜索任务
            cursor.execute("""
                SELECT id, title, description, assignee, status
                FROM office_tasks 
                WHERE title ILIKE %s OR description ILIKE %s
                ORDER BY created_at DESC
                LIMIT 5
            """, (search_pattern, search_pattern))
            
            tasks = []
            for row in cursor.fetchall():
                tasks.append({
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "assignee": row[3],
                    "status": row[4]
                })
            
            # 搜索会议
            cursor.execute("""
                SELECT id, title, description, start_time, location
                FROM office_schedule 
                WHERE title ILIKE %s OR description ILIKE %s
                ORDER BY start_time DESC
                LIMIT 5
            """, (search_pattern, search_pattern))
            
            meetings = []
            for row in cursor.fetchall():
                meetings.append({
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "start_time": row[3].isoformat() if row[3] else None,
                    "location": row[4]
                })
            
            return {
                "tasks": tasks,
                "meetings": meetings,
                "total_tasks": len(tasks),
                "total_meetings": len(meetings)
            }
        except Exception as e:
            return {
                "error": str(e),
                "message": f"搜索时出错: {e}",
                "tasks": [],
                "meetings": []
            }
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取办公统计数据
        
        Returns:
            dict: 统计数据
        """
        try:
            conn = self.postgres_client.get_connection()
            if not conn:
                return {
                    "error": "Database not connected",
                    "message": "数据库未连接，无法获取统计数据"
                }
                
            cursor = conn.cursor()
            
            # 获取任务统计
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_tasks,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tasks,
                    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_tasks,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_tasks
                FROM office_tasks
            """)
            
            task_stats = cursor.fetchone()
            
            # 获取今日会议数
            cursor.execute("""
                SELECT COUNT(*) 
                FROM office_schedule 
                WHERE DATE(start_time) = CURRENT_DATE
            """)
            
            today_meetings = cursor.fetchone()[0]
            
            return {
                "tasks": {
                    "total": task_stats[0] if task_stats[0] else 0,
                    "completed": task_stats[1] if task_stats[1] else 0,
                    "in_progress": task_stats[2] if task_stats[2] else 0,
                    "pending": task_stats[3] if task_stats[3] else 0
                },
                "today_meetings": today_meetings,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "message": f"获取统计数据时出错: {e}"
            }
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def close(self):
        """
        关闭代理连接
        """
        try:
            self.postgres_client.close()
        except:
            pass
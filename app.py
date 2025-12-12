from flask import Flask, render_template, request, jsonify
from workflows.research_workflow import ResearchWorkflow
import threading
import queue
import uuid

app = Flask(__name__)

# 存储报告结果的字典
reports = {}

# 存储对话历史的字典
conversations = {}

class ReportGenerator(threading.Thread):
    def __init__(self, topic, report_id):
        threading.Thread.__init__(self)
        self.topic = topic
        self.report_id = report_id
        
    def run(self):
        try:
            # 创建研究工作流实例
            workflow = ResearchWorkflow()
            
            # 运行研究流程
            report = workflow.run_research_process(self.topic)
            
            # 保存报告结果
            reports[self.report_id] = {
                'status': 'completed',
                'data': report
            }
            
            # 关闭连接
            workflow.close()
        except Exception as e:
            reports[self.report_id] = {
                'status': 'error',
                'error': str(e)
            }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_report', methods=['POST'])
def generate_report():
    data = request.get_json()
    topic = data.get('topic', '')
    
    if not topic:
        return jsonify({'error': '请输入研究主题'}), 400
    
    # 生成唯一的报告ID
    report_id = str(uuid.uuid4())
    
    # 初始化报告状态
    reports[report_id] = {
        'status': 'processing',
        'data': None
    }
    
    # 启动后台线程生成报告
    generator = ReportGenerator(topic, report_id)
    generator.start()
    
    return jsonify({'report_id': report_id})

@app.route('/report_status/<report_id>')
def report_status(report_id):
    if report_id in reports:
        return jsonify(reports[report_id])
    else:
        return jsonify({'status': 'not_found'}), 404

# 新增多轮对话路由
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    conversation_id = data.get('conversation_id', str(uuid.uuid4()))
    
    if not user_message:
        return jsonify({'error': '消息不能为空'}), 400
    
    # 初始化对话历史
    if conversation_id not in conversations:
        conversations[conversation_id] = []
    
    # 将用户消息添加到对话历史
    conversations[conversation_id].append({
        'role': 'user',
        'content': user_message
    })
    
    try:
        # 创建研究工作流实例
        workflow = ResearchWorkflow()
        
        # 处理用户消息（这里简化处理，实际可以根据消息内容进行不同操作）
        if any(keyword in user_message.lower() for keyword in ['研究', '报告', '分析']):
            # 如果用户请求研究报告，则启动研究流程
            report = workflow.run_research_process(user_message)
            ai_response = f"我已经为您生成了关于'{user_message}'的研究报告:\n\n{report['content']}"
        else:
            # 简单的对话回复
            ai_response = f"您说的是: '{user_message}'。如果您需要关于这个主题的研究报告，请告诉我具体的研究方向。"
        
        # 关闭连接
        workflow.close()
        
        # 将AI回复添加到对话历史
        conversations[conversation_id].append({
            'role': 'assistant',
            'content': ai_response
        })
        
        return jsonify({
            'conversation_id': conversation_id,
            'message': ai_response
        })
    except Exception as e:
        return jsonify({'error': f'处理消息时出错: {str(e)}'}), 500

@app.route('/conversation/<conversation_id>')
def get_conversation(conversation_id):
    if conversation_id in conversations:
        return jsonify({
            'conversation_id': conversation_id,
            'messages': conversations[conversation_id]
        })
    else:
        return jsonify({'error': '对话不存在'}), 404

'''
#=============================================================================
# 下面是使用 FastAPI 的现代化实现版本（注释掉，仅供对比参考）
#=============================================================================

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, List
import asyncio

# 创建 FastAPI 应用实例
app_fastapi = FastAPI(title="AI研究助手", description="基于FastAPI的AI研究助手API")

# 数据模型定义
class ReportRequest(BaseModel):
    topic: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ReportResponse(BaseModel):
    report_id: str

class StatusResponse(BaseModel):
    status: str
    data: Optional[dict] = None
    error: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    message: str

class ConversationResponse(BaseModel):
    conversation_id: str
    messages: List[Dict[str, str]]

# 存储报告结果和对话历史的字典（实际项目中应使用数据库）
reports_fastapi: Dict[str, dict] = {}
conversations_fastapi: Dict[str, list] = {}

# 后台任务函数
async def generate_report_task(topic: str, report_id: str):
    try:
        # 创建研究工作流实例
        workflow = ResearchWorkflow()
        
        # 运行研究流程
        report = workflow.run_research_process(topic)
        
        # 保存报告结果
        reports_fastapi[report_id] = {
            'status': 'completed',
            'data': report
        }
        
        # 关闭连接
        workflow.close()
    except Exception as e:
        reports_fastapi[report_id] = {
            'status': 'error',
            'error': str(e)
        }

@app_fastapi.post("/generate_report", response_model=ReportResponse)
async def generate_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """生成研究报告"""
    if not request.topic:
        raise HTTPException(status_code=400, detail="请输入研究主题")
    
    # 生成唯一的报告ID
    report_id = str(uuid.uuid4())
    
    # 初始化报告状态
    reports_fastapi[report_id] = {
        'status': 'processing',
        'data': None
    }
    
    # 添加后台任务生成报告
    background_tasks.add_task(generate_report_task, request.topic, report_id)
    
    return ReportResponse(report_id=report_id)

@app_fastapi.get("/report_status/{report_id}", response_model=StatusResponse)
async def report_status(report_id: str):
    """获取报告状态"""
    if report_id in reports_fastapi:
        return StatusResponse(**reports_fastapi[report_id])
    else:
        raise HTTPException(status_code=404, detail="报告未找到")

@app_fastapi.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """处理聊天消息"""
    user_message = request.message
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    if not user_message:
        raise HTTPException(status_code=400, detail="消息不能为空")
    
    # 初始化对话历史
    if conversation_id not in conversations_fastapi:
        conversations_fastapi[conversation_id] = []
    
    # 将用户消息添加到对话历史
    conversations_fastapi[conversation_id].append({
        'role': 'user',
        'content': user_message
    })
    
    try:
        # 创建研究工作流实例
        workflow = ResearchWorkflow()
        
        # 处理用户消息（这里简化处理，实际可以根据消息内容进行不同操作）
        if any(keyword in user_message.lower() for keyword in ['研究', '报告', '分析']):
            # 如果用户请求研究报告，则启动研究流程
            report = workflow.run_research_process(user_message)
            ai_response = f"我已经为您生成了关于'{user_message}'的研究报告:\n\n{report['content']}"
        else:
            # 简单的对话回复
            ai_response = f"您说的是: '{user_message}'。如果您需要关于这个主题的研究报告，请告诉我具体的研究方向。"
        
        # 关闭连接
        workflow.close()
        
        # 将AI回复添加到对话历史
        conversations_fastapi[conversation_id].append({
            'role': 'assistant',
            'content': ai_response
        })
        
        return ChatResponse(conversation_id=conversation_id, message=ai_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'处理消息时出错: {str(e)}')

@app_fastapi.get("/conversation/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    """获取对话历史"""
    if conversation_id in conversations_fastapi:
        return ConversationResponse(
            conversation_id=conversation_id,
            messages=conversations_fastapi[conversation_id]
        )
    else:
        raise HTTPException(status_code=404, detail="对话不存在")

@app_fastapi.get("/", response_class=HTMLResponse)
async def read_root():
    """根路径，返回前端页面"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

# 如果需要运行 FastAPI 应用，请取消下面的注释并使用 uvicorn 运行:
# uvicorn app:app_fastapi --host 0.0.0.0 --port 8000 --reload
'''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
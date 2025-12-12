from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, List
import asyncio
import uuid
from workflows.research_workflow import ResearchWorkflow

# 创建 FastAPI 应用实例
app = FastAPI(title="AI研究助手", description="基于FastAPI的AI研究助手API")

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
reports: Dict[str, dict] = {}
conversations: Dict[str, list] = {}

# 后台任务函数
async def generate_report_task(topic: str, report_id: str):
    try:
        # 创建研究工作流实例
        workflow = ResearchWorkflow()
        
        # 运行研究流程
        report = workflow.run_research_process(topic)
        
        # 保存报告结果
        reports[report_id] = {
            'status': 'completed',
            'data': report
        }
        
        # 关闭连接
        workflow.close()
    except Exception as e:
        reports[report_id] = {
            'status': 'error',
            'error': str(e)
        }

@app.post("/generate_report", response_model=ReportResponse)
async def generate_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """生成研究报告"""
    if not request.topic:
        raise HTTPException(status_code=400, detail="请输入研究主题")
    
    # 生成唯一的报告ID
    report_id = str(uuid.uuid4())
    
    # 初始化报告状态
    reports[report_id] = {
        'status': 'processing',
        'data': None
    }
    
    # 添加后台任务生成报告
    background_tasks.add_task(generate_report_task, request.topic, report_id)
    
    return ReportResponse(report_id=report_id)

@app.get("/report_status/{report_id}", response_model=StatusResponse)
async def report_status(report_id: str):
    """获取报告状态"""
    if report_id in reports:
        return StatusResponse(**reports[report_id])
    else:
        raise HTTPException(status_code=404, detail="报告未找到")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """处理聊天消息"""
    user_message = request.message
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    if not user_message:
        raise HTTPException(status_code=400, detail="消息不能为空")
    
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
        
        return ChatResponse(conversation_id=conversation_id, message=ai_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'处理消息时出错: {str(e)}')

@app.get("/conversation/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    """获取对话历史"""
    if conversation_id in conversations:
        return ConversationResponse(
            conversation_id=conversation_id,
            messages=conversations[conversation_id]
        )
    else:
        raise HTTPException(status_code=404, detail="对话不存在")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """根路径，返回前端页面"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
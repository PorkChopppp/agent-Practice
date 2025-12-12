# 办公助理 Agent 文档

办公助理 Agent 是一个专为提升办公效率而设计的智能助手，可以处理日常办公任务并通过飞书平台与用户进行交互。

## 功能特性

### 1. 任务管理
- 创建新任务
- 查看任务列表
- 更新任务状态
- 分配任务给团队成员

### 2. 日程管理
- 安排会议
- 查看近期事件
- 会议提醒

### 3. 信息查询
- 搜索任务和会议
- 获取办公统计数据

### 4. 飞书集成
- 通过飞书机器人接收指令
- 发送消息和通知
- 处理回调事件

## 使用方法

### 1. 飞书命令
在飞书中可以通过以下命令与办公助理交互：

```
📌 创建任务 <标题> [负责人] [优先级1-3] [截止日期YYYY-MM-DD] - 创建新任务
📌 我的任务 [状态] - 查看分配给我的任务
📌 任务状态 <任务ID> <状态> - 更新任务状态(pending/in_progress/completed)
📌 安排会议 <标题> <开始时间> <结束时间> <参会人1,参会人2> [地点] - 安排会议
📌 近期事件 [天数] - 查看近期的会议和任务
📌 搜索 <关键词> - 搜索任务和会议
📌 统计 - 查看办公统计数据
📌 help - 显示帮助信息
```

### 2. API 接口
办公助理也提供 RESTful API 接口，可以通过 HTTP 请求调用各项功能。

## 配置说明

### 环境变量
在 `.env` 文件中添加以下配置项：

```env
# 飞书配置
FEISHU_APP_ID=your_feishu_app_id
FEISHU_APP_SECRET=your_feishu_app_secret
FEISHU_WEBHOOK_URL=your_feishu_webhook_url
```

### 数据库表结构

办公助理使用 PostgreSQL 存储任务和日程信息：

1. `office_tasks` 表 - 存储任务信息
2. `office_schedule` 表 - 存储会议日程

## 代码结构

```
agents/
  └── office_assistant_agent.py    # 办公助理核心逻辑
integrations/
  └── feishu_integration.py        # 飞书集成模块
handlers/
  └── feishu_handler.py            # 飞书消息处理器
routes/
  └── feishu_routes.py             # 飞书API路由
```

## 扩展开发

可以通过以下方式扩展办公助理的功能：

1. 添加新的命令处理函数
2. 扩展数据库表结构
3. 增加与其他办公平台的集成
4. 实现更复杂的任务调度算法
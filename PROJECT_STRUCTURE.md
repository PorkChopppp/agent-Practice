# 项目结构说明

```
.
├── .docker/                    # Docker配置文件
│   └── docker-compose.yml     # Docker Compose配置
├── .github/                   # GitHub相关配置
│   └── workflows/            # GitHub Actions工作流
├── agents/                    # AI代理模块
│   ├── knowledge_agent.py     # 知识管理代理
│   ├── orchestrator_agent.py  # 协调者代理
│   ├── office_assistant_agent.py  # 办公助理代理
│   ├── researcher_agent.py    # 研究员代理
│   ├── review_agent.py        # 评审代理
│   └── writer_agent.py        # 作家代理
├── config/                    # 配置文件
│   └── settings.py           # 应用配置
├── database/                  # 数据库相关
│   ├── milvus_client.py      # Milvus客户端
│   └── postgres_client.py    # PostgreSQL客户端
├── docs/                      # 文档
│   ├── OFFICE_ASSISTANT.md   # 办公助理文档
│   └── ...                   # 其他文档
├── handlers/                  # 消息处理器
│   └── feishu_handler.py     # 飞书消息处理器
├── integrations/              # 第三方集成
│   └── feishu_integration.py # 飞书集成模块
├── routes/                    # API路由
│   └── feishu_routes.py      # 飞书API路由
├── templates/                 # Web模板
│   └── index.html            # 主页模板
├── workflows/                 # 工作流
│   └── research_workflow.py   # 研究工作流
├── .env.example               # 环境变量示例
├── .gitignore                 # Git忽略文件
├── app.py                     # Flask应用主文件
├── app_fastapi.py             # FastAPI应用主文件
├── main.py                    # 命令行应用主文件
├── requirements.txt           # Python依赖
└── README.md                  # 项目说明
```

## 主要模块说明

### agents/ - AI代理模块
包含各种AI代理的实现，每个代理负责特定的任务。

### config/ - 配置文件
存放应用的配置信息。

### database/ - 数据库相关
包含数据库客户端的实现。

### docs/ - 文档
项目的详细文档。

### handlers/ - 消息处理器
处理来自不同平台的消息。

### integrations/ - 第三方集成
与第三方平台的集成模块。

### routes/ - API路由
定义API的路由和处理逻辑。

### templates/ - Web模板
Web界面的模板文件。

### workflows/ - 工作流
定义复杂的工作流程。

## 核心文件说明

- `app.py`: Flask Web应用入口
- `app_fastapi.py`: FastAPI Web应用入口
- `main.py`: 命令行应用入口
- `requirements.txt`: Python依赖列表
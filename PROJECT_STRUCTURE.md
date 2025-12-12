# 项目结构说明

## 总体目录结构

```
ai-research-assistant/
├── agents/                     # AI代理模块
├── config/                     # 配置管理
├── database/                   # 数据库客户端
├── milvus_data/                # Milvus数据存储目录
├── templates/                  # Web前端模板
├── tests/                      # 测试文件
├── workflows/                  # 工作流定义
├── .docker/                    # Docker相关配置文件
├── .env                        # 环境变量配置
├── .env.example                # 环境变量配置示例
├── app.py                      # Web应用入口
├── main.py                     # 命令行程序入口
├── requirements.txt            # 项目依赖
├── POSTGRESQL_SETUP.md         # PostgreSQL设置指南
└── README.md                   # 项目说明文档
```

## 各目录详细说明

### agents/ - AI代理模块
- [researcher_agent.py](file:///D:/PythonProject3/agents/researcher_agent.py) - 研究员代理，负责收集信息
- [writer_agent.py](file:///D:/PythonProject3/agents/writer_agent.py) - 作家代理，负责生成报告

### config/ - 配置管理
- [settings.py](file:///D:/PythonProject3/config/settings.py) - 应用配置，从环境变量加载配置参数

### database/ - 数据库客户端
- [milvus_client.py](file:///D:/PythonProject3/database/milvus_client.py) - Milvus向量数据库客户端
- [postgres_client.py](file:///D:/PythonProject3/database/postgres_client.py) - PostgreSQL关系数据库客户端

### milvus_data/ - Milvus数据存储目录
- [docker-compose.yml](file:///D:/PythonProject3/milvus_data/docker-compose.yml) - Milvus Docker编排文件
- [volumes/](file:///D:/PythonProject3/milvus_data/volumes/) - Milvus数据卷

### templates/ - Web前端模板
- [index.html](file:///D:/PythonProject3/templates/index.html) - 主页模板

### tests/ - 测试文件
- [test_connection.py](file:///D:/PythonProject3/tests/test_connection.py) - 连接测试
- [test_connection2.py](file:///D:/PythonProject3/tests/test_connection2.py) - 连接测试2
- [test_db.py](file:///D:/PythonProject3/tests/test_db.py) - 数据库测试
- [test_db_detailed.py](file:///D:/PythonProject3/tests/test_db_detailed.py) - 详细数据库测试
- [test_openai.py](file:///D:/PythonProject3/tests/test_openai.py) - OpenAI测试
- [test_siliconflow.py](file:///D:/PythonProject3/tests/test_siliconflow.py) - SiliconFlow测试
- [text.py](file:///D:/PythonProject3/tests/text.py) - 文本测试

### workflows/ - 工作流定义
- [research_workflow.py](file:///D:/PythonProject3/workflows/research_workflow.py) - 研究工作流，协调研究员和作家代理的工作流程

### .docker/ - Docker相关配置文件
- postgres/[init.sql](file:///D:/PythonProject3/.docker/postgres/init.sql) - PostgreSQL数据库初始化脚本

## 核心应用文件

### 主要入口点
- [app.py](file:///D:/PythonProject3/app.py) - Web应用入口，提供基于Flask的Web界面
- [main.py](file:///D:/PythonProject3/main.py) - 命令行程序入口，提供命令行接口

### 配置文件
- [.env](file:///D:/PythonProject3/.env) - 环境变量配置文件（需自行创建）
- [.env.example](file:///D:/PythonProject3/.env.example) - 环境变量配置示例
- [requirements.txt](file:///D:/PythonProject3/requirements.txt) - Python依赖包列表

### 文档文件
- [README.md](file:///D:/PythonProject3/README.md) - 项目说明文档
- [POSTGRESQL_SETUP.md](file:///D:/PythonProject3/POSTGRESQL_SETUP.md) - PostgreSQL设置指南
- [PROJECT_STRUCTURE.md](file:///D:/PythonProject3/PROJECT_STRUCTURE.md) - 项目结构说明（本文档）

## 数据文件

### 数据库文件
- [research_assistant.db](file:///D:/PythonProject3/research_assistant.db) - SQLite数据库文件（备用存储）
- [milvus_data.json](file:///D:/PythonProject3/milvus_data.json) - Milvus数据备份文件

这些文件用于在无法连接到实际数据库时提供本地存储功能。
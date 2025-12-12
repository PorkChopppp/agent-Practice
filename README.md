# AI研究助手

这是一个基于AI的自动化研究助手，能够根据给定主题进行研究并生成结构化报告。

## 功能特性

- 自动研究指定主题
- 生成结构化的研究报告
- 使用向量数据库(Milvus)存储和检索信息
- 使用关系数据库(PostgreSQL)存储最终报告
- 支持OpenAI GPT模型生成内容
- 提供Web界面方便用户交互
- 支持FastAPI和Flask两种Web框架实现

## 技术栈

- Python 3.8+
- LangChain - 构建AI应用的框架
- OpenAI API - 大语言模型和嵌入模型
- Milvus - 向量数据库，用于相似性搜索
- PostgreSQL - 关系数据库，用于存储结构化数据
- Docker - 容器化部署
- Flask/FastAPI - Web应用框架

## 系统架构

```
+------------------+     +------------------+     +------------------+
|  Research Agent  |<--->|  Vector Store    |     |  Report Storage  |
| (信息收集代理)    |     | (Milvus向量库)    |     | (PostgreSQL)     |
+------------------+     +------------------+     +------------------+
         ^                        ^                        ^
         |                        |                        |
         v                        v                        v
+------------------+     +------------------+     +------------------+
|   Writer Agent   |<--->|  LLM (GPT)       |<--->|   Configuration  |
| (报告生成代理)    |     | (大语言模型)      |     |   (配置管理)      |
+------------------+     +------------------+     +------------------+
```

## 项目目录结构

```
ai-research-assistant/
├── agents/                     # AI代理模块
│   ├── researcher_agent.py     # 研究员代理，负责收集信息
│   └── writer_agent.py         # 作家代理，负责生成报告
├── config/                     # 配置管理
│   └── settings.py             # 应用配置
├── database/                   # 数据库客户端
│   ├── milvus_client.py        # Milvus客户端
│   └── postgres_client.py      # PostgreSQL客户端
├── milvus_data/                # Milvus数据存储目录
│   ├── docker-compose.yml      # Milvus Docker编排文件
│   └── volumes/                # Milvus数据卷
├── templates/                  # Web前端模板
│   └── index.html              # 主页模板
├── tests/                      # 测试文件
│   ├── test_connection.py      # 连接测试
│   ├── test_connection2.py     # 连接测试2
│   ├── test_db.py              # 数据库测试
│   ├── test_db_detailed.py     # 详细数据库测试
│   ├── test_openai.py          # OpenAI测试
│   ├── test_siliconflow.py     # SiliconFlow测试
│   └── text.py                 # 文本测试
├── workflows/                  # 工作流定义
│   └── research_workflow.py    # 研究工作流
├── .docker/                    # Docker相关配置文件
│   └── postgres/               # PostgreSQL初始化脚本
│       └── init.sql            # PostgreSQL数据库初始化脚本
├── .env                        # 环境变量配置
├── .env.example                # 环境变量配置示例
├── app.py                      # Flask Web应用入口
├── app_fastapi.py              # FastAPI Web应用入口
├── main.py                     # 命令行程序入口
├── requirements.txt            # 项目依赖
├── PROJECT_STRUCTURE.md        # 项目结构详细说明
└── README.md                   # 项目说明文档
```

## 安装和配置

### 1. 克隆项目

```bash
git clone <repository-url>
cd ai-research-assistant
```

### 2. 创建虚拟环境并安装依赖

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 3. 配置环境变量

复制 [.env.example](file:///D:/PythonProject3/.env.example) 文件并重命名为 [.env](file:///D:/PythonProject3/.env)：

```bash
cp .env.example .env
```

编辑 [.env](file:///D:/PythonProject3/.env) 文件，填入您的配置信息：

```env
# OpenAI API密钥
OPENAI_API_KEY=your-openai-api-key

# Milvus配置
MILVUS_HOST=localhost
MILVUS_PORT=19530
USE_MILVUS=true

# PostgreSQL配置
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DB=research_assistant
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
```

## 启动数据库服务

使用Docker启动Milvus和PostgreSQL：

```bash
# 启动Milvus
docker-compose -f milvus_data/docker-compose.yml up -d

# 启动PostgreSQL
docker run -d --name postgres_research \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_DB=research_assistant \
  -p 5432:5432 \
  postgres:15
```

## 使用方法

### 命令行方式

运行主程序：

```bash
python main.py "研究主题"
```

例如：

```bash
python main.py "人工智能发展趋势"
```

如果没有提供主题，程序将默认使用"人工智能"作为研究主题。

### Web界面方式

项目支持两种Web框架实现：

#### Flask版本

```bash
python app.py
```

#### FastAPI版本

```bash
uvicorn app_fastapi:app --host 0.0.0.0 --port 8000 --reload
```

然后在浏览器中访问 `http://localhost:5000` (Flask) 或 `http://localhost:8000` (FastAPI)，通过图形界面输入研究主题并查看生成的报告。

## 故障排除

### 地区限制问题

如果您看到如下错误信息：
```
Error code: 403 - {'error': {'code': 'unsupported_country_region_territory', 'message': 'Country, region, or territory not supported'}}
```

这表明您的地区不受OpenAI API支持。您可以考虑以下解决方案：

1. 使用代理服务器连接到支持的地区
2. 使用其他兼容的API服务提供商（如Azure OpenAI、DeepSeek等）
3. 在支持的地区部署应用程序

### 数据库连接问题

如果遇到数据库连接问题，请检查：

1. Docker容器是否正在运行：
   ```bash
   docker ps
   ```

2. 数据库连接参数是否正确配置在 [.env](file:///D:/PythonProject3/.env) 文件中

3. 防火墙设置是否阻止了数据库端口连接

### Milvus连接问题

如果Milvus连接失败，程序会自动切换到本地文件存储模式，不会影响基本功能。

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](file:///D:/PythonProject3/LICENSE) 文件了解详情。
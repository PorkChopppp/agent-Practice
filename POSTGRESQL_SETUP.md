# PostgreSQL 连接测试指南

本文档提供了多种方式来测试和设置 PostgreSQL 数据库连接。

## 1. 当前环境检查

首先，检查是否已有 PostgreSQL 容器在运行：

```bash
docker ps | grep postgres
```

如果没有运行中的 PostgreSQL 容器，则需要启动一个新的容器。

## 2. 使用 Docker 启动 PostgreSQL

### 2.1 正常网络环境下

如果网络连接正常，可以使用以下命令启动 PostgreSQL 容器：

```bash
docker run -d \
  --name research-assistant-postgres \
  -e POSTGRES_DB=research_assistant \
  -e POSTGRES_USER=researcher \
  -e POSTGRES_PASSWORD=research_pass \
  -p 5432:5432 \
  postgres:13
```

### 2.2 网络受限环境下

如果无法直接从 Docker Hub 拉取镜像，可以尝试以下方法：

1. **配置 Docker 国内镜像源**

   在 Docker Desktop 中配置国内镜像源：
   - 打开 Docker Desktop 设置
   - 进入 Docker Engine 选项卡
   - 添加以下配置：
   ```json
   {
     "registry-mirrors": [
       "https://hub-mirror.c.163.com",
       "https://mirror.baidubce.com"
     ]
   }
   ```
   - 点击 Apply & Restart 重启 Docker

2. **手动下载并导入镜像**

   在能访问 Docker Hub 的机器上执行：
   ```bash
   docker pull postgres:13
   docker save postgres:13 -o postgres-13.tar
   ```
   
   将 postgres-13.tar 文件拷贝到目标机器，然后执行：
   ```bash
   docker load -i postgres-13.tar
   ```

## 3. 测试数据库连接

### 3.1 修改配置文件

确保 `.env` 文件中有正确的数据库配置：

```env
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_USER=researcher
POSTGRES_PASSWORD=research_pass
POSTGRES_DB=research_assistant
```

### 3.2 运行测试脚本

使用现有的测试脚本：

```bash
python test_db.py
```

或者单独测试 PostgreSQL 连接：

```bash
python -c "
import psycopg2
from config.settings import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

try:
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    print('✅ 成功连接到 PostgreSQL 数据库')
    conn.close()
except Exception as e:
    print(f'❌ 连接失败: {e}')
"
```

## 4. 故障排除

### 4.1 常见错误及解决方案

1. **Connection refused**
   - 确保 PostgreSQL 容器正在运行
   - 检查端口映射是否正确（-p 5432:5432）
   - 确认防火墙没有阻止连接

2. **Authentication failed**
   - 检查用户名和密码是否正确
   - 确认数据库名称是否正确

3. **Timeout**
   - 检查网络连接
   - 增加连接超时时间

### 4.2 查看容器日志

如果容器启动但无法连接，可以查看日志：

```bash
docker logs research-assistant-postgres
```

### 4.3 进入容器调试

进入容器内部进行调试：

```bash
docker exec -it research-assistant-postgres bash
```

在容器内可以使用 psql 命令行工具：

```bash
psql -U researcher -d research_assistant
```

## 5. 替代方案

如果暂时无法使用 PostgreSQL，系统会自动降级到内存存储模式，不影响基本功能使用。
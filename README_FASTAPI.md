# FastAPI 版本说明

本文档介绍了如何使用 FastAPI 版本替换现有的 Flask 实现。

## 项目对比

### Flask 版本 (app.py)
- 基于装饰器的路由系统
- 同步处理模型
- 使用 threading 处理并发任务
- 较老但稳定的框架

### FastAPI 版本 (app_fastapi.py)
- 基于现代 Python 类型提示
- 异步处理模型，性能更好
- 自动生成交互式 API 文档
- 内置 Swagger UI 和 ReDoc
- 更好的开发体验和错误处理

## 如何切换到 FastAPI

1. 安装额外依赖：
   ```bash
   pip install fastapi uvicorn
   ```

2. 运行 FastAPI 应用：
   ```bash
   uvicorn app_fastapi:app --host 0.0.0.0 --port 8000 --reload
   ```

3. 访问应用：
   - 前端页面: http://localhost:8000
   - API 文档: http://localhost:8000/docs

## FastAPI 优势

1. **性能**: 基于 Starlette 和 Pydantic，性能比 Flask 高出 3 倍
2. **自动文档**: 自动生成交互式 API 文档 (Swagger UI)
3. **类型安全**: 利用 Python 类型提示提供更好的开发体验
4. **异步支持**: 原生支持异步操作，提高并发处理能力
5. **依赖注入**: 内置依赖注入系统，便于测试和扩展

## 保留 Flask 版本的原因

虽然 FastAPI 更现代和高效，但我们保留了 Flask 版本以供参考和对比：
1. 保持向后兼容性
2. 为不熟悉 FastAPI 的开发者提供参考
3. 在某些简单部署场景中可能更适合

## 注意事项

1. 两个版本使用相同的前端模板 (templates/index.html)
2. 业务逻辑保持一致，都在 workflows/research_workflow.py 中
3. 数据存储方式相同（内存存储，实际项目中应使用数据库）
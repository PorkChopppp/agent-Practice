import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 从环境变量获取API密钥
api_key = os.getenv("OPENAI_API_KEY")

def test_siliconflow_connection():
    print("测试硅基流动(SiliconFlow) API连接...")
    print(f"API密钥前缀: {api_key[:10]}..." if api_key else "未找到API密钥")
    
    if not api_key:
        print("错误: 未找到API密钥")
        return
    
    try:
        # 创建使用硅基流动API的客户端
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.siliconflow.cn/v1"
        )
        
        # 测试嵌入模型（使用bge模型）
        print("测试嵌入模型...")
        embedding_response = client.embeddings.create(
            model="BAAI/bge-large-zh-v1.5",
            input="测试文本"
        )
        print(f"嵌入模型测试成功，维度: {len(embedding_response.data[0].embedding)}")
        
        # 测试聊天模型（使用Qwen模型）
        print("测试聊天模型...")
        chat_response = client.chat.completions.create(
            model="Qwen/Qwen2-7B-Instruct",
            messages=[
                {"role": "system", "content": "你是一个有帮助的助手。"},
                {"role": "user", "content": "你好世界"}
            ],
            max_tokens=10
        )
        print(f"聊天模型测试成功，回复: {chat_response.choices[0].message.content}")
        
    except Exception as e:
        print(f"硅基流动API连接测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_siliconflow_connection()
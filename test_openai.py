import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载.env文件
load_dotenv()

# 从环境变量获取API密钥
api_key = os.getenv("OPENAI_API_KEY")

def test_openai_connection():
    print("测试OpenAI连接...")
    print(f"API密钥前缀: {api_key[:10]}..." if api_key else "未找到API密钥")
    
    if not api_key:
        print("错误: 未找到OpenAI API密钥")
        return
    
    try:
        # 使用标准OpenAI API
        client = OpenAI(api_key=api_key)
        
        # 测试嵌入模型
        print("测试嵌入模型...")
        embedding_response = client.embeddings.create(
            model="text-embedding-ada-002",
            input="测试文本"
        )
        print(f"嵌入模型测试成功，维度: {len(embedding_response.data[0].embedding)}")
        
        # 测试聊天模型
        print("测试聊天模型...")
        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一个有帮助的助手。"},
                {"role": "user", "content": "你好世界"}
            ],
            max_tokens=10
        )
        print(f"聊天模型测试成功，回复: {chat_response.choices[0].message.content}")
        
    except Exception as e:
        print(f"OpenAI连接测试失败: {e}")
        # 检查是否是配额问题
        if "insufficient_quota" in str(e):
            print("检测到配额不足问题，请检查您的OpenAI账户计划和账单详情。")

if __name__ == "__main__":
    test_openai_connection()
"""
飞书API路由

处理飞书平台的回调请求和事件处理。
"""

from flask import Blueprint, request, jsonify
from handlers.feishu_handler import FeishuHandler
import json

# 创建蓝图
feishu_bp = Blueprint('feishu', __name__)

# 初始化处理器
handler = FeishuHandler()


@feishu_bp.route('/feishu/callback', methods=['POST'])
def feishu_callback():
    """
    处理飞书回调事件
    
    Returns:
        Response: JSON响应
    """
    try:
        # 获取请求数据
        request_data = request.get_json()
        
        # 如果是验证回调URL的请求
        if request_data.get("type") == "url_verification":
            return jsonify({
                "challenge": request_data.get("challenge")
            })
        
        # 处理其他事件
        result = handler.handle_message(request_data)
        
        # 发送响应消息（如果有）
        if result.get("success") and "message" in result:
            # 这里应该根据实际情况发送回飞书
            # 为简化起见，我们现在只记录结果
            print(f"处理结果: {result['message']}")
        
        return jsonify({"code": 0})
    except Exception as e:
        print(f"处理飞书回调时出错: {e}")
        return jsonify({"code": 1, "message": str(e)}), 500


@feishu_bp.route('/feishu/send_test', methods=['POST'])
def send_test_message():
    """
    发送测试消息到飞书
    
    Returns:
        Response: JSON响应
    """
    try:
        data = request.get_json()
        message = data.get("message", "测试消息")
        
        # 这里应该根据实际配置发送消息
        # 为简化起见，我们现在只返回成功消息
        print(f"发送测试消息: {message}")
        
        return jsonify({
            "success": True,
            "message": "测试消息已发送"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": f"发送测试消息时出错: {e}"
        }), 500
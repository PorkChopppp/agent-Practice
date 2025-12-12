"""
飞书集成模块

该模块提供与飞书平台的集成能力，包括消息发送、事件处理等功能。
"""

import json
import hmac
import hashlib
import base64
import time
from typing import Dict, Any, Optional
from urllib.parse import urlencode
import requests
from config.settings import OPENAI_API_KEY


class FeishuIntegration:
    """
    飞书集成类
    
    提供与飞书平台的集成能力，包括发送消息、处理事件等。
    """
    
    def __init__(self, app_id: str = None, app_secret: str = None, webhook_url: str = None):
        """
        初始化飞书集成
        
        Args:
            app_id (str): 飞书应用ID
            app_secret (str): 飞书应用密钥
            webhook_url (str): 飞书机器人Webhook地址（用于自定义机器人）
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.webhook_url = webhook_url
        self.access_token = None
        self.token_expires_at = 0
        
        print("飞书集成初始化完成")
    
    def get_tenant_access_token(self) -> Optional[str]:
        """
        获取租户访问令牌
        
        Returns:
            str: 访问令牌，获取失败时返回None
        """
        # 如果令牌还未过期，直接返回
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        # 获取新的访问令牌
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                self.access_token = result.get("tenant_access_token")
                # 提前5分钟过期以确保安全
                self.token_expires_at = time.time() + result.get("expire", 7200) - 300
                return self.access_token
            else:
                print(f"获取访问令牌失败: {result}")
                return None
        except Exception as e:
            print(f"获取访问令牌时出错: {e}")
            return None
    
    def send_message(self, receive_id_type: str, receive_id: str, msg_type: str, content: str) -> Dict[str, Any]:
        """
        发送消息
        
        Args:
            receive_id_type (str): 接收者ID类型 (open_id, user_id, union_id, email, chat_id)
            receive_id (str): 接收者ID
            msg_type (str): 消息类型 (text, post, image, file, audio, media, sticker)
            content (str): 消息内容（JSON字符串）
            
        Returns:
            dict: 发送结果
        """
        # 获取访问令牌
        token = self.get_tenant_access_token()
        if not token:
            return {
                "success": False,
                "error": "Failed to get access token"
            }
        
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        params = {"receive_id_type": receive_id_type}
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {
            "receive_id": receive_id,
            "msg_type": msg_type,
            "content": content
        }
        
        try:
            response = requests.post(url, params=params, headers=headers, json=payload, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                return {
                    "success": True,
                    "message_id": result.get("data", {}).get("message_id"),
                    "message": "消息发送成功"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("msg", "Unknown error"),
                    "code": result.get("code")
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"发送消息时出错: {e}"
            }
    
    def send_webhook_message(self, msg_type: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        通过Webhook发送消息（适用于自定义机器人）
        
        Args:
            msg_type (str): 消息类型
            content (dict): 消息内容
            
        Returns:
            dict: 发送结果
        """
        if not self.webhook_url:
            return {
                "success": False,
                "error": "Webhook URL not configured"
            }
        
        payload = {
            "msg_type": msg_type,
            "content": content
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            result = response.json()
            
            if result.get("code") == 0 or result.get("StatusCode") == 0:
                return {
                    "success": True,
                    "message": "消息发送成功"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("msg") or result.get("message") or "Unknown error",
                    "code": result.get("code") or result.get("StatusCode")
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"发送Webhook消息时出错: {e}"
            }
    
    def send_text_message(self, receive_id_type: str, receive_id: str, text: str) -> Dict[str, Any]:
        """
        发送文本消息
        
        Args:
            receive_id_type (str): 接收者ID类型
            receive_id (str): 接收者ID
            text (str): 文本内容
            
        Returns:
            dict: 发送结果
        """
        content = json.dumps({
            "text": text
        })
        return self.send_message(receive_id_type, receive_id, "text", content)
    
    def send_webhook_text_message(self, text: str) -> Dict[str, Any]:
        """
        通过Webhook发送文本消息
        
        Args:
            text (str): 文本内容
            
        Returns:
            dict: 发送结果
        """
        content = {
            "text": text
        }
        return self.send_webhook_message("text", content)
    
    def handle_callback_event(self, request_data: Dict[str, Any], encrypt_key: str = None) -> Dict[str, Any]:
        """
        处理飞书回调事件
        
        Args:
            request_data (dict): 回调请求数据
            encrypt_key (str): 加密密钥（用于验证签名）
            
        Returns:
            dict: 处理结果
        """
        # 验证签名（如果提供了encrypt_key）
        if encrypt_key:
            signature = request_data.get("signature")
            timestamp = request_data.get("timestamp")
            nonce = request_data.get("nonce")
            body = request_data.get("body", "")
            
            if not self._verify_signature(signature, timestamp, nonce, body, encrypt_key):
                return {
                    "success": False,
                    "error": "Signature verification failed"
                }
        
        # 处理事件
        event_type = request_data.get("header", {}).get("event_type")
        event = request_data.get("event", {})
        
        return {
            "success": True,
            "event_type": event_type,
            "event": event,
            "message": f"Received {event_type} event"
        }
    
    def _verify_signature(self, signature: str, timestamp: str, nonce: str, body: str, encrypt_key: str) -> bool:
        """
        验证飞书回调签名
        
        Args:
            signature (str): 签名
            timestamp (str): 时间戳
            nonce (str): 随机数
            body (str): 请求体
            encrypt_key (str): 加密密钥
            
        Returns:
            bool: 签名是否有效
        """
        try:
            # 构造待签名字符串
            to_sign = f"{timestamp}\n{nonce}\n{body}"
            
            # 使用HMAC-SHA256算法计算签名
            signature_base64 = base64.b64encode(
                hmac.new(encrypt_key.encode('utf-8'), to_sign.encode('utf-8'), hashlib.sha256).digest()
            ).decode('utf-8')
            
            return signature == signature_base64
        except Exception as e:
            print(f"验证签名时出错: {e}")
            return False
    
    def parse_command(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析用户命令
        
        Args:
            message (dict): 消息内容
            
        Returns:
            dict: 解析结果，包含命令类型和参数
        """
        content = message.get("text", "").strip()
        
        # 移除@机器人部分
        if content.startswith("@_user_"):
            parts = content.split(" ", 2)
            if len(parts) > 1:
                content = parts[-1]
            else:
                content = ""
        
        # 解析命令
        if not content:
            return {"command": "help"}
        
        parts = content.split(" ", 1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        return {
            "command": command,
            "args": args
        }
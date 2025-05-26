from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import httpx
import json
import random
import re
from src.config.settings import settings
from typing import Dict, Any, Optional, List, Union

class OpenAIService:
    def __init__(self, instances=None):
        self.instances = instances if instances is not None else settings.instances
        self.all_instances = list(self.instances) if instances is not None else list(settings.instances)
        # 创建一个持久的 httpx.AsyncClient 实例
        self.client = httpx.AsyncClient(
            timeout=600.0,
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            http2=True  # 启用 HTTP/2 以提高性能
        )

    async def forward_full_request(self, method: str, path: str, body: Any = None, headers: Dict[str, str] = None, tried_instances=None) -> Dict[str, Any]:
        """
        将完整请求（包括方法、路径、请求体和头信息）转发到 Azure OpenAI API
        
        Args:
            method: HTTP 方法 (GET, POST, etc.)
            path: 完整API路径，包括查询参数
            body: 请求体 (对于POST, PUT等请求)
            headers: 请求头
            tried_instances: 已尝试过的实例名称列表
            
        Returns:
            Azure OpenAI API的响应
        """
        if not self.instances:
            raise HTTPException(status_code=500, detail="No OpenAI instances configured")
        
        # 初始化已尝试实例列表
        if tried_instances is None:
            tried_instances = []
            # 初始化存储最后错误的变量
            self.last_error_response = None
        
        # 获取未尝试过的实例
        available_instances = [instance for instance in self.instances if instance['name'] not in tried_instances]
        
        # 如果所有实例都已尝试过，返回最后一个错误
        if not available_instances:
            # 直接返回保存的最后一个错误响应
            if hasattr(self, 'last_error_response') and self.last_error_response:
                return self.last_error_response
            else:
                raise HTTPException(status_code=502, detail="All OpenAI instances failed")
            
        instance = random.choice(available_instances)
        tried_instances.append(instance['name'])
        
        try:
            # 获取基础URL
            base_url = instance['url'].rstrip('/')
            
            # 规范化路径 - 确保没有重复部分
            # 1. 检查是否有重复的 'openai/' 前缀
            normalized_path = path
            if normalized_path.startswith('/'):
                normalized_path = normalized_path[1:]
                
            # 2. 检查是否有多个 'openai/' 出现
            # 只保留第一个 'openai/' 及其后面的内容
            if normalized_path.startswith('openai/'):
                openai_parts = normalized_path.split('openai/', 1)
                if len(openai_parts) > 1:
                    normalized_path = f"openai/{openai_parts[1]}"
            else:
                # 如果路径不是以 openai/ 开头，添加它
                normalized_path = f"openai/{normalized_path}"
                
            # 构建最终URL
            full_url = f"{base_url}/{normalized_path}"
            
            # 过滤掉一些不应转发的请求头
            excluded_headers = [
                'host', 
                'content-length', 
                'connection',
                'accept-encoding'
            ]
            
            # 准备请求头
            request_headers = {
                k: v for k, v in (headers or {}).items() 
                if k.lower() not in excluded_headers
            }
            
            # 添加 Azure OpenAI 验证头
            request_headers["api-key"] = instance['api_key']
            if "content-type" not in request_headers:
                request_headers["content-type"] = "application/json"
            
            print(f"Sending {method} request to: {full_url}")
            
            # 发送请求时使用类级别的客户端
            try:
                response = await self.client.request(
                    method=method,
                    url=full_url,
                    json=body if isinstance(body, (dict, list)) else None,
                    content=body if not isinstance(body, (dict, list)) else None,
                    headers=request_headers
                )
                response.raise_for_status()
                
                # 尝试解析为JSON，如果失败则返回原始文本
                try:
                    return response.json()
                except:
                    return {"text": response.text}
                
            except httpx.HTTPStatusError as e:
                # 记录错误
                self.handle_error(e, instance)
                
                # 保存原始错误响应
                try:
                    # 直接使用原始响应对象
                    status_code = e.response.status_code
                    content_type = e.response.headers.get('content-type', '')
                    
                    # 根据内容类型解析响应
                    if 'application/json' in content_type:
                        response_data = e.response.json()
                        # 添加额外的元数据
                        response_data["_azure_openai_instance"] = instance["name"]
                        response_data["_azure_openai_status_code"] = status_code
                        self.last_error_response = response_data
                    else:
                        # 如果不是JSON，构造一个包含原始文本的JSON
                        self.last_error_response = {
                            "error": {
                                "message": e.response.text,
                                "code": status_code,
                                "_azure_openai_instance": instance["name"]
                            }
                        }
                except Exception as parse_error:
                    # 处理无法解析响应的情况
                    self.last_error_response = {
                        "error": {
                            "message": str(e),
                            "type": "http_error",
                            "code": getattr(e.response, 'status_code', 500),
                            "_azure_openai_instance": instance["name"]
                        }
                    }
                
                # 尝试下一个实例
                return await self.forward_full_request(method, path, body, headers, tried_instances)
            
        except Exception as e:
            # 记录其他类型错误
            self.handle_error(e, instance)
            
            # 存储错误信息
            self.last_error_response = {
                "error": {
                    "message": str(e),
                    "type": "runtime_error",
                    "_azure_openai_instance": instance["name"]
                }
            }
            
            # 尝试下一个实例
            return await self.forward_full_request(method, path, body, headers, tried_instances)

    # 保留原有的方法以兼容旧代码
    async def forward_request(self, payload: dict, endpoint_path: str = None, tried_instances=None) -> Dict[str, Any]:
        """原有方法的兼容性包装"""
        headers = {"Content-Type": "application/json"}
        return await self.forward_full_request("POST", endpoint_path, payload, headers, tried_instances)

    async def forward_streaming_request(self, method: str, path: str, body: Any = None, headers: Dict[str, str] = None, tried_instances=None):
        """处理流式请求，如聊天完成的流式响应"""
        if not self.instances:
            raise HTTPException(status_code=500, detail="No OpenAI instances configured")
        
        # 初始化已尝试实例列表
        if tried_instances is None:
            tried_instances = []
    
        # 获取未尝试过的实例
        available_instances = [instance for instance in self.instances if instance['name'] not in tried_instances]
        
        if not available_instances:
            raise HTTPException(status_code=502, detail="All OpenAI instances failed")
        
        instance = random.choice(available_instances)
        tried_instances.append(instance['name'])
        
        try:
            # 获取基础URL
            base_url = instance['url'].rstrip('/')
            
            # 规范化路径 - 确保没有重复部分
            # 1. 检查是否有重复的 'openai/' 前缀
            normalized_path = path
            if normalized_path.startswith('/'):
                normalized_path = normalized_path[1:]
                
            # 2. 检查是否有多个 'openai/' 出现
            # 只保留第一个 'openai/' 及其后面的内容
            if normalized_path.startswith('openai/'):
                openai_parts = normalized_path.split('openai/', 1)
                if len(openai_parts) > 1:
                    normalized_path = f"openai/{openai_parts[1]}"
            else:
                # 如果路径不是以 openai/ 开头，添加它
                normalized_path = f"openai/{normalized_path}"
                
            # 构建最终URL
            full_url = f"{base_url}/{normalized_path}"
            
            # 过滤掉一些不应转发的请求头
            excluded_headers = [
                'host', 
                'content-length', 
                'connection',
                'accept-encoding'
            ]
            
            # 准备请求头
            request_headers = {
                k: v for k, v in (headers or {}).items() 
                if k.lower() not in excluded_headers
            }
            
            # 添加 Azure OpenAI 验证头
            request_headers["api-key"] = instance['api_key']
            if "content-type" not in request_headers:
                request_headers["content-type"] = "application/json"
            
            # 确保请求 stream=true
            if isinstance(body, dict):
                body["stream"] = True
            
            async def stream_generator():
                async with httpx.AsyncClient(timeout=600.0) as client:
                    async with client.stream(
                        method=method,
                        url=full_url,
                        json=body,
                        headers=request_headers
                    ) as response:
                        if response.status_code != 200:
                            # 非流式错误处理
                            error_content = await response.read()
                            try:
                                error_json = json.loads(error_content)
                                yield json.dumps(error_json)
                            except:
                                yield json.dumps({"error": {"message": error_content.decode('utf-8')}})
                            return
                        
                        # 处理流式响应
                        async for line in response.aiter_lines():
                            if line.strip():
                                # 过滤流式响应格式
                                line = re.sub(r'^data: ', '', line)
                                if line != "[DONE]":
                                    yield line + "\n"
            
            return StreamingResponse(
                stream_generator(),
                media_type="text/event-stream"
            )
            
        except Exception as e:
            # 如果当前实例失败，尝试下一个
            if len(tried_instances) < len(self.instances):
                return await self.forward_streaming_request(method, path, body, headers, tried_instances)
            else:
                raise HTTPException(status_code=502, detail=str(e))

    def handle_error(self, error, instance):
        error_message = str(error)
        status_code = None
        response_text = None
        
        # 尝试提取 HTTP 状态码和响应内容
        if hasattr(error, 'response'):
            status_code = error.response.status_code
            try:
                response_text = error.response.text
            except:
                response_text = "无法读取响应内容"
                
        print(f"Error with instance {instance['name']}: {status_code} - {response_text or error_message}")

    def log_request(self, endpoint: str, payload: dict):
        # 实现日志记录逻辑
        # 可以移除敏感信息后再记录
        sanitized_payload = payload.copy() if isinstance(payload, dict) else {"data": str(payload)[:100] + "..."}
        if isinstance(sanitized_payload, dict) and "api_key" in sanitized_payload:
            sanitized_payload["api_key"] = "***"
            
        print(f"Request to {endpoint} with payload: {json.dumps(sanitized_payload)}")

    # 在类中添加关闭方法
    async def close(self):
        await self.client.aclose()
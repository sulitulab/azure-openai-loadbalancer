from fastapi import FastAPI, Request, HTTPException, Response, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.middleware.logging_middleware import LoggingMiddleware
from src.config.settings import settings
from src.services.openai_service import OpenAIService
import json
import time
import os
from typing import Optional

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(LoggingMiddleware)

# 从环境变量获取API密钥
API_KEY = os.environ.get("API_KEY", "")
security = HTTPBearer()

# 添加一个依赖函数来验证API密钥
async def verify_api_key(authorization: Optional[str] = Header(None)):
    if not API_KEY:
        # 如果没有设置API密钥，则不执行验证
        return False
    
    if not authorization:
        raise HTTPException(
            status_code=401, 
            detail={"error": {"message": "认证失败: 缺少Authorization头", "code": "unauthorized"}}
        )
    
    # 检查Authorization头的格式
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401, 
            detail={"error": {"message": "认证失败: Authorization头格式不正确，应为'Bearer YOUR_API_KEY'", "code": "unauthorized"}}
        )
    
    token = parts[1]
    if token != API_KEY:
        raise HTTPException(
            status_code=401, 
            detail={"error": {"message": "认证失败: API密钥无效", "code": "unauthorized"}}
        )
    
    return True

# 添加事件处理器
@app.on_event("startup")
async def startup_event():
    # 初始化服务
    app.state.openai_service = OpenAIService(settings.instances)

@app.on_event("shutdown")
async def shutdown_event():
    # 关闭客户端连接
    await app.state.openai_service.close()

# 添加在主路由前
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "timestamp": time.time()}

@app.get("/openai/health")
async def openai_health_check():
    """OpenAI路径健康检查端点"""
    if not settings.instances:
        return Response(
            content=json.dumps({"status": "warning", "message": "No OpenAI instances configured"}),
            status_code=200,
            media_type="application/json"
        )
    return {"status": "ok", "instances_count": len(settings.instances)}

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def forward_any_request(full_path: str, request: Request, authenticated: bool = Depends(verify_api_key)):
    """
    完全透传API请求到 Azure OpenAI 后端
    
    例如：
    如果客户端请求是 https://127.0.0.1/openai/deployments/gpt4o/chat/completions?api-version=2025-01-01-preview
    将被转发到后端的：
    https://{instance_url}/openai/deployments/gpt4o/chat/completions?api-version=2025-01-01-preview
    
    需要通过 Authorization: Bearer YOUR_API_KEY 头进行认证
    """
    try:
        # 获取查询参数
        query_string = request.url.query
        
        # 构建完整路径，包括查询参数
        complete_path = full_path
        if query_string:
            complete_path = f"{full_path}?{query_string}"

        # 获取请求体 (如果有)
        request_body = {}
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                request_body = await request.json()
            except:
                # 如果不是JSON格式，尝试获取原始内容
                request_body = await request.body()
                
        # 获取请求头
        headers = dict(request.headers)
        
        # 检查是否为流式请求
        is_streaming = False
        if request.method == "POST" and isinstance(request_body, dict) and request_body.get("stream") == True:
            is_streaming = True
        
        # 根据请求类型选择转发方法
        if is_streaming:
            return await app.state.openai_service.forward_streaming_request(
                method=request.method,
                path=complete_path,
                body=request_body,
                headers=headers
            )
        else:
            response = await app.state.openai_service.forward_full_request(
                method=request.method,
                path=complete_path,
                body=request_body,
                headers=headers
            )
            
        # 检查是否有错误响应
        if isinstance(response, dict) and "error" in response:
            # 从错误响应中提取状态码
            status_code = response.get("_azure_openai_status_code", 500)
            # 删除我们添加的元数据字段，保持原始响应格式
            if "_azure_openai_status_code" in response:
                del response["_azure_openai_status_code"]
            if "_azure_openai_instance" in response:
                del response["_azure_openai_instance"]
                
            # 返回原始状态码和错误响应
            return Response(
                content=json.dumps(response),
                status_code=status_code,
                media_type="application/json"
            )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
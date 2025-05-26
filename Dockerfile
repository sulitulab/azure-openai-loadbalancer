FROM --platform=linux/amd64 python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    # 创建必要的目录并设置适当的权限
    mkdir -p /app/logs /config && \
    chmod -R 755 /app/logs /config

# 复制应用代码和默认配置
COPY ./src ./src
COPY ./config/openai_instances.json /config/openai_instances.json

# 定义卷挂载点
VOLUME ["/config", "/app/logs"]

# 设置环境变量
ENV OPENAI_CONFIG_PATH=/config/openai_instances.json
ENV LOG_LEVEL=INFO
ENV LOG_FILE=/app/logs/app.log
ENV PYTHONUNBUFFERED=1

# 创建非 root 用户以提高安全性
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app /config /app/logs

# 切换到非 root 用户
USER appuser

# 暴露应用端口
EXPOSE 8000


# 运行应用
CMD ["python", "-m", "src.main"]
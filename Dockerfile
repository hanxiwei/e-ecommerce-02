# 使用 Playwright 官方 Python 镜像，内置了浏览器运行环境
FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码和测试代码
COPY ./app /app/app
COPY ./tests /app/tests

# 安装浏览器（镜像已包含依赖，只需下载浏览器二进制文件）
RUN playwright install chromium

# 暴露端口
EXPOSE 8000

# 启动应用的命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

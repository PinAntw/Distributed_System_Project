# 使用 Python 基礎映像
FROM python:3.12

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 和本地依賴包
COPY requirements.txt .
COPY packages/ ./packages/

# 安裝依賴（從本地包安裝）
RUN pip install --no-cache-dir --find-links=./packages -r requirements.txt

# 複製應用代碼
COPY . .

# 暴露端口（默認 Cloud Run 端口 8080）
EXPOSE 8080

# 啟動應用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

# 使用官方 Python 運行時作為父映像
FROM python:3.9-slim-buster

# 設定工作目錄
WORKDIR /app

# 將當前目錄內容複製到容器的 /app 目錄中
COPY . /app

# 安裝任何必要的套件
RUN pip install --no-cache-dir -r requirements.txt

# 讓容器監聽連接埠 5000
EXPOSE 5000

# 當容器啟動時運行 app.py
CMD ["python", "app.py"]
from flask import Flask, request, jsonify, render_template 
import psycopg2 # <--- 更改這裡：使用 psycopg2 連接 PostgreSQL

app = Flask(__name__)

# --- 需要更改 ---
# 替換為您的 Aurora PostgreSQL 寫入器執行個體的終端節點
DB_HOST = "moodle-aurora-cluster.cluster-cgbabjkj7tny.us-east-1.rds.amazonaws.com"
# 替換為您的 Aurora PostgreSQL 用戶名 (通常是 postgres)
DB_USER = "moodleadmin"
# 替換為您的 Aurora PostgreSQL 密碼
DB_PASSWORD = "55439147zhjf"
# 替換為您在 Aurora PostgreSQL 中創建的資料庫名稱
DB_NAME = "moodle-aurora-cluster"
# --- 更改結束 ---


def get_db_connection():
    try:
        # For PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# 新增一個主頁路由，用於顯示表單和資料
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        message = request.form.get('message_text') # 從表單獲取數據
        if not message:
            # 簡單錯誤處理，實際應用中可以做得更完善
            messages = get_all_messages()
            return render_template('index.html', error="請輸入訊息！", messages=messages)

        conn = get_db_connection()
        if conn is None:
            messages = get_all_messages()
            return render_template('index.html', error="資料庫連接失敗！", messages=messages)

        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO messages (message_text) VALUES (%s)"
                cursor.execute(sql, (message,))
            conn.commit()
            # 插入成功後，重定向到 GET 請求，以避免重複提交
            return render_template('index.html', success="訊息已成功儲存！", messages=get_all_messages())
        except Exception as e:
            conn.rollback()
            messages = get_all_messages()
            return render_template('index.html', error=f"儲存失敗：{e}", messages=messages)
        finally:
            conn.close()
    else: # GET 請求
        messages = get_all_messages()
        return render_template('index.html', messages=messages)

# 輔助函數：獲取所有訊息
def get_all_messages():
    conn = get_db_connection()
    if conn is None:
        return [] # 如果連接失敗，返回空列表

    try:
        with conn.cursor() as cursor:
            sql = "SELECT id, message_text, created_at FROM messages ORDER BY created_at DESC"
            cursor.execute(sql)
            result = []
            for row in cursor.fetchall():
                result.append({
                    "id": row[0],
                    "message_text": row[1],
                    "created_at": row[2].strftime("%Y-%m-%d %H:%M:%S") # 格式化時間
                })
        return result
    except Exception as e:
        print(f"Error reading from database: {e}")
        return []
    finally:
        conn.close()

# 移除原有的 /create 和 /read 路由，因為它們的功能已經整合到 '/' 路由中
# @app.route('/create', methods=['POST'])
# def create_data():
#     ...

# @app.route('/read', methods=['GET'])
# def read_data():
#     ...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
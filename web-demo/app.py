from flask import Flask, request, jsonify
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

@app.route('/')
def index():
    return "Welcome to the Web Demo! Try /create and /read."

@app.route('/create', methods=['POST'])
def create_data():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Message field is required"}), 400

    message = data['message']
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            # PostgreSQL 使用 %s 作為參數佔位符
            sql = "INSERT INTO messages (message_text) VALUES (%s)"
            cursor.execute(sql, (message,))
        conn.commit()
        return jsonify({"status": "success", "message": "Data created successfully"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/read', methods=['GET'])
def read_data():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            sql = "SELECT id, message_text, created_at FROM messages ORDER BY created_at DESC"
            cursor.execute(sql)
            # psycopg2 fetchall() 返回元組列表，需要手動轉換為字典
            result = []
            for row in cursor.fetchall():
                result.append({
                    "id": row[0],
                    "message_text": row[1],
                    "created_at": row[2].isoformat() # 將 datetime 對象轉換為 ISO 格式字符串
                })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
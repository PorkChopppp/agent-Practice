import psycopg2

try:
    conn = psycopg2.connect(
        host='127.0.0.1',
        port=5432,
        dbname='research_assistant',
        user='researcher',
        password='password123'
    )
    print("连接成功，密码正确")
    conn.close()
except Exception as e:
    print("连接失败:", e)
